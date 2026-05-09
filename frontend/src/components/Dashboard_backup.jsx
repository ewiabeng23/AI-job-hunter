import { useState, useEffect } from 'react'
import axios from 'axios'
import './Dashboard.css'

const API_URL = 'http://3.82.138.233:31678/api'

function Dashboard({ user, token, onLogout }) {
  const [activeTab, setActiveTab] = useState('search')
  const [cvs, setCvs] = useState([])
  const [jobs, setJobs] = useState([])
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(false)
  
  // CV state
  const [cvName, setCvName] = useState('')
  const [cvContent, setCvContent] = useState('')
  const [showCvForm, setShowCvForm] = useState(false)
  
  // Search state
  const [jobTitle, setJobTitle] = useState('DevOps Engineer')
  const [location, setLocation] = useState('London, UK')
  const [minSalary, setMinSalary] = useState(60000)
  const [maxSalary, setMaxSalary] = useState(150000)
  const [keywords, setKeywords] = useState('AWS, Docker, Kubernetes')
  
  // Selected job
  const [selectedJob, setSelectedJob] = useState(null)
  const [applying, setApplying] = useState(false)

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  }

  useEffect(() => {
    loadCvs()
    loadApplications()
  }, [])

  const loadCvs = async () => {
    try {
      const response = await axios.get(`${API_URL}/cvs`, axiosConfig)
      setCvs(response.data)
    } catch (err) {
      console.error('Failed to load CVs:', err)
    }
  }

  const loadApplications = async () => {
    try {
      const response = await axios.get(`${API_URL}/applications`, axiosConfig)
      setApplications(response.data)
    } catch (err) {
      console.error('Failed to load applications:', err)
    }
  }

  const createCV = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await axios.post(`${API_URL}/cvs`, {
        name: cvName,
        content: cvContent,
        is_default: cvs.length === 0
      }, axiosConfig)
      
      setCvName('')
      setCvContent('')
      setShowCvForm(false)
      loadCvs()
      alert('✅ CV created successfully!')
    } catch (err) {
      alert('❌ Failed to create CV')
    } finally {
      setLoading(false)
    }
  }

  const searchJobs = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const response = await axios.post(`${API_URL}/jobs/search`, {
        filters: {
          job_title: jobTitle,
          location: location,
          min_salary: minSalary,
          max_salary: maxSalary,
          keywords: keywords.split(',').map(k => k.trim()),
          max_results: 20
        }
      }, axiosConfig)
      
      setJobs(response.data.jobs)
    } catch (err) {
      alert('❌ Failed to search jobs')
    } finally {
      setLoading(false)
    }
  }

  const applyToJob = async (job) => {
    if (cvs.length === 0) {
      alert('⚠️ Please create a CV first!')
      setActiveTab('cvs')
      return
    }

    setApplying(true)
    setSelectedJob(job)
    
    try {
      const response = await axios.post(`${API_URL}/jobs/apply`, {
        job_data: {
          title: job.title,
          company: job.company,
          description: job.description,
          url: job.url,
          source: job.source || 'Indeed'
        }
      }, axiosConfig)
      
      alert(`✅ Application submitted! Match score: ${response.data.match?.match_score}%`)
      loadApplications()
    } catch (err) {
      if (err.response?.status === 403) {
        alert('⚠️ Free tier limit reached (5 applications/month). Upgrade to Pro!')
      } else {
        alert('❌ Failed to apply')
      }
    } finally {
      setApplying(false)
      setSelectedJob(null)
    }
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <h1>🚀 Job Hunter AI</h1>
          <div className="user-info">
            <span>👤 {user?.full_name || user?.email}</span>
            <span className="tier-badge">{user?.subscription_tier?.toUpperCase()}</span>
            <span className="usage">📊 {user?.applications_this_month || 0}/5 apps used</span>
            <button onClick={onLogout} className="btn-logout">Logout</button>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="tabs">
        <button 
          className={activeTab === 'search' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('search')}
        >
          🔍 Search Jobs
        </button>
        <button 
          className={activeTab === 'cvs' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('cvs')}
        >
          📄 My CVs ({cvs.length})
        </button>
        <button 
          className={activeTab === 'applications' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('applications')}
        >
          📊 Applications ({applications.length})
        </button>
      </div>

      {/* Content */}
      <div className="dashboard-content">
        
        {/* SEARCH TAB */}
        {activeTab === 'search' && (
          <div className="tab-content">
            <div className="search-section">
              <h2>🎯 Find Your Dream Job</h2>
              <form onSubmit={searchJobs} className="search-form">
                <div className="form-row">
                  <div className="form-group">
                    <label>Job Title</label>
                    <input
                      type="text"
                      value={jobTitle}
                      onChange={(e) => setJobTitle(e.target.value)}
                      placeholder="e.g., DevOps Engineer"
                    />
                  </div>
                  <div className="form-group">
                    <label>Location</label>
                    <input
                      type="text"
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                      placeholder="e.g., London, UK"
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Min Salary (£)</label>
                    <input
                      type="number"
                      value={minSalary}
                      onChange={(e) => setMinSalary(Number(e.target.value))}
                    />
                  </div>
                  <div className="form-group">
                    <label>Max Salary (£)</label>
                    <input
                      type="number"
                      value={maxSalary}
                      onChange={(e) => setMaxSalary(Number(e.target.value))}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Keywords (comma-separated)</label>
                  <input
                    type="text"
                    value={keywords}
                    onChange={(e) => setKeywords(e.target.value)}
                    placeholder="e.g., AWS, Docker, Kubernetes"
                  />
                </div>

                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? '🔄 Searching...' : '🚀 Search Jobs'}
                </button>
              </form>
            </div>

            {/* Jobs Results */}
            {jobs.length > 0 && (
              <div className="jobs-section">
                <h3>📋 Found {jobs.length} Jobs</h3>
                <div className="jobs-grid">
                  {jobs.map((job) => (
                    <div key={job.id} className="job-card">
                      <div className="job-header">
                        <h4>{job.title}</h4>
                        <span className="job-score">🎯 Score: {job.relevance_score}</span>
                      </div>
                      <p className="job-company">🏢 {job.company}</p>
                      <p className="job-location">📍 {job.location} | 🌐 {job.remote}</p>
                      <p className="job-salary">💰 {job.salary}</p>
                      <p className="job-posted">📅 {job.posted_days_ago}d ago</p>
                      {job.keyword_matches > 0 && (
                        <p className="job-keywords">🔑 {job.keyword_matches} keywords match</p>
                      )}
                      <button 
                        onClick={() => applyToJob(job)}
                        className="btn-apply"
                        disabled={applying && selectedJob?.id === job.id}
                      >
                        {applying && selectedJob?.id === job.id ? '🔄 Applying...' : '✨ Apply with AI'}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* CVS TAB */}
        {activeTab === 'cvs' && (
          <div className="tab-content">
            <div className="cvs-header">
              <h2>📄 My CVs</h2>
              <button 
                className="btn-primary"
                onClick={() => setShowCvForm(!showCvForm)}
              >
                {showCvForm ? '❌ Cancel' : '➕ Add New CV'}
              </button>
            </div>

            {showCvForm && (
              <form onSubmit={createCV} className="cv-form">
                <div className="form-group">
                  <label>CV Name</label>
                  <input
                    type="text"
                    value={cvName}
                    onChange={(e) => setCvName(e.target.value)}
                    placeholder="e.g., Tech CV"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>CV Content</label>
                  <textarea
                    value={cvContent}
                    onChange={(e) => setCvContent(e.target.value)}
                    placeholder="Paste your CV here..."
                    rows={15}
                    required
                  />
                </div>
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? '🔄 Saving...' : '💾 Save CV'}
                </button>
              </form>
            )}

            <div className="cvs-list">
              {cvs.map((cv) => (
                <div key={cv.id} className="cv-card">
                  <h4>{cv.name} {cv.is_default && <span className="default-badge">⭐ Default</span>}</h4>
                  <p className="cv-preview">{cv.content.substring(0, 200)}...</p>
                  <p className="cv-date">Created: {new Date(cv.created_at).toLocaleDateString()}</p>
                </div>
              ))}
              {cvs.length === 0 && !showCvForm && (
                <p className="empty-state">No CVs yet. Click "Add New CV" to get started!</p>
              )}
            </div>
          </div>
        )}

        {/* APPLICATIONS TAB */}
        {activeTab === 'applications' && (
          <div className="tab-content">
            <h2>📊 My Applications</h2>
            <div className="applications-list">
              {applications.map((app) => (
                <div key={app.id} className="application-card">
                  <div className="app-header">
                    <h4>{app.job_title}</h4>
                    <span className="app-score">Match: {app.match_score}%</span>
                  </div>
                  <p className="app-company">🏢 {app.company}</p>
                  <p className="app-status">Status: <span className={`status-${app.status}`}>{app.status}</span></p>
                  <p className="app-date">Applied: {new Date(app.applied_at).toLocaleDateString()}</p>
                  {app.job_url && (
                    <a href={app.job_url} target="_blank" rel="noopener noreferrer" className="btn-link">
                      🔗 View Job
                    </a>
                  )}
                </div>
              ))}
              {applications.length === 0 && (
                <p className="empty-state">No applications yet. Start searching for jobs!</p>
              )}
            </div>
          </div>
        )}

      </div>
    </div>
  )
}

export default Dashboard
