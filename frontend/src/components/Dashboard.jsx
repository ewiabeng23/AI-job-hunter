import { useState, useEffect } from 'react'
import { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, BorderStyle } from 'docx'
import { saveAs } from 'file-saver'
import axios from 'axios'
import './Dashboard.css'
import InterviewPrep from './InterviewPrep'

const API_URL = 'https://jobhunter.wigsbydiko.co.uk/api'

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
  const [jobTitle, setJobTitle] = useState('')
  const [location, setLocation] = useState('')
  const [minSalary, setMinSalary] = useState('')
  const [maxSalary, setMaxSalary] = useState('')
  const [keywords, setKeywords] = useState('')
  const [easyApplyOnly, setEasyApplyOnly] = useState(false)
  
  // Selected job
  const [selectedJob, setSelectedJob] = useState(null)
  const [applying, setApplying] = useState(false)
  
  // Modal for showing tailored CV
  const [showModal, setShowModal] = useState(false)
  const [modalData, setModalData] = useState(null)
  const [showInterviewPrep, setShowInterviewPrep] = useState(false)
  const [interviewPrepJob, setInterviewPrepJob] = useState(null)

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


  const deleteApplication = async (appId) => {
    if (!window.confirm("Delete this application?")) return
    try {
      await axios.delete(`${API_URL}/applications/${appId}`, axiosConfig)
      loadApplications()
      alert("✅ Application deleted!")
    } catch (err) {
      alert("❌ Failed to delete")
    }
  }

  const deleteCV = async (cvId) => {
    if (!window.confirm("Delete this CV?")) return
    try {
      await axios.delete(`${API_URL}/cvs/${cvId}`, axiosConfig)
      loadCvs()
      alert("✅ CV deleted!")
    } catch (err) {
      alert("❌ Failed to delete")
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
          max_results: 20,
          easy_apply_only: easyApplyOnly
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
      
      // Show the AI-tailored CV and cover letter in modal
      setModalData({
        job: job,
        customCV: response.data.custom_cv,
        coverLetter: response.data.cover_letter,
        matchScore: response.data.match?.match_score,
        recommendation: response.data.match?.recommendation
      })
      setShowModal(true)
      
      loadApplications()
    } catch (err) {
      if (err.response?.status === 403) {
        alert('⚠️ Free tier limit reached (5 applications/month). Upgrade to Pro!')
      } else {
        alert('❌ Failed to apply: ' + (err.response?.data?.detail || err.message))
      }
    } finally {
      setApplying(false)
      setSelectedJob(null)
    }
  }

  const downloadCV = async () => {
    if (!modalData?.customCV) return
    try {
      const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, BorderStyle } = await import('docx')
      const { saveAs } = await import('file-saver')
      const cvLines = modalData.customCV.split('\n').filter(l => l.trim())
      const docParagraphs = cvLines.map(line => {
        const trimmed = line.trim()
        const isHeader = trimmed === trimmed.toUpperCase() && trimmed.length > 3 && trimmed.length < 50
        const isSubHeader = trimmed.endsWith(':') && trimmed.length < 60
        if (isHeader) {
          return new Paragraph({
            text: trimmed,
            heading: HeadingLevel.HEADING_2,
            spacing: { before: 240, after: 120 }
          })
        } else if (isSubHeader) {
          return new Paragraph({
            children: [new TextRun({ text: trimmed, bold: true, size: 24 })],
            spacing: { before: 160, after: 80 }
          })
        } else if (trimmed.startsWith('-') || trimmed.startsWith('\u2022')) {
          return new Paragraph({
            text: trimmed.replace(/^[-\u2022]\s*/, ''),
            bullet: { level: 0 },
            spacing: { after: 60 }
          })
        } else {
          return new Paragraph({
            children: [new TextRun({ text: trimmed, size: 22 })],
            spacing: { after: 80 }
          })
        }
      })
      const doc = new Document({
        sections: [{ properties: {}, children: [
          new Paragraph({
            children: [new TextRun({ text: modalData.job.title + ' — ' + modalData.job.company, bold: true, size: 28 })],
            alignment: AlignmentType.CENTER,
            spacing: { after: 400 }
          }),
          ...docParagraphs
        ]}]
      })
      const blob = await Packer.toBlob(doc)
      saveAs(blob, `CV_${modalData.job.company}_${modalData.job.title}.docx`)
    } catch(err) {
      console.error('docx error:', err)
      const blob = new Blob([modalData.customCV], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `CV_${modalData.job.company}_${modalData.job.title}.txt`
      a.click()
    }
  }

  const downloadCoverLetter = () => {
    if (!modalData?.coverLetter) return
    
    const blob = new Blob([modalData.coverLetter], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `CoverLetter_${modalData.job.company}_${modalData.job.title}.txt`
    a.click()
  }

  const proceedToApply = () => {
    if (modalData?.job?.url) {
      window.open(modalData.job.url, '_blank')
      setShowModal(false)
      alert('✅ Your tailored CV and cover letter are downloaded! Good luck! 🍀')
    }
  }

  return (
    <div className="dashboard">
      {/* Modal for showing AI-tailored CV */}
      {showModal && modalData && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>🎯 AI-Tailored Application</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>✕</button>
            </div>
            
            <div className="modal-body">
              <div className="match-section">
                <h3>Match Score: <span className="score">{modalData.matchScore}%</span></h3>
                <p className="recommendation">Recommendation: <strong>{modalData.recommendation}</strong></p>
              </div>

              <div className="cv-section">
                <div className="section-header">
                  <h3>📄 Custom CV (Tailored for {modalData.job.company})</h3>
                  <button onClick={downloadCV} className="btn-download">⬇️ Download CV</button>
                </div>
                
              </div>

              <div className="cover-section">
                <div className="section-header">
                  <h3>✉️ Cover Letter</h3>
                  <button onClick={downloadCoverLetter} className="btn-download">⬇️ Download Cover Letter</button>
                </div>
                
              </div>

              <div className="modal-footer">
                <p className="info-text">
                  ✅ Your CV and cover letter are ready! Download them and click "Apply Now" to submit your application.
                </p>
                <button onClick={proceedToApply} className="btn-apply-now">
                  🚀 Apply Now at {modalData.job.company}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <h1>🚀 Job Hunter</h1>
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
        <button 
          className={activeTab === 'interview' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('interview')}
        >
          🎤 Interview Prep
        </button>

      {/* Content */}
      <div className="dashboard-content">
        
        {/* SEARCH TAB */}
        {activeTab === 'search' && (
          <div className="tab-content">
            <div className="search-section">
              <h2>🎯 Find Your Dream Job</h2>
              <p className="subtitle">Our AI will automatically tailor your CV for each job!</p>
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

                <div className="form-group easy-apply-toggle">
                  <label className="toggle-label">
                    <input
                      type="checkbox"
                      checked={easyApplyOnly}
                      onChange={(e) => setEasyApplyOnly(e.target.checked)}
                    />
                    ⚡ Easy Apply only (jobs with simple 1-click application)
                  </label>
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
                      {job.easy_apply && (
                        <span className="easy-apply-badge">⚡ Easy Apply</span>
                      )}
                      <button 
                        onClick={() => applyToJob(job)}
                        className="btn-apply"
                        disabled={applying && selectedJob?.id === job.id}
                      >
                        {applying && selectedJob?.id === job.id ? '🔄 Tailoring CV...' : '✨ Apply'}
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
              <div>
                <h2>📄 My CVs</h2>
                <p className="subtitle">Upload your master CV - AI will tailor it for each job!</p>
              </div>
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
                    placeholder="e.g., Tech CV, Finance CV"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>CV Content (Paste your full CV here)</label>
                  <textarea
                    value={cvContent}
                    onChange={(e) => setCvContent(e.target.value)}
                    placeholder="Paste your complete CV here. The AI will automatically customize it for each job you apply to..."
                    rows={15}
                    required
                  />
                </div>
                <div className="form-group easy-apply-toggle">
                  <label className="toggle-label">
                    <input
                      type="checkbox"
                      checked={easyApplyOnly}
                      onChange={(e) => setEasyApplyOnly(e.target.checked)}
                    />
                    ⚡ Easy Apply only (jobs with simple 1-click application)
                  </label>
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
                  <button onClick={() => deleteCV(cv.id)} className="btn-delete">🗑️ Delete</button>
                  <p className="cv-note">💡 This CV will be AI-tailored for each job you apply to</p>
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
            <p className="subtitle">Each application has an AI-tailored CV specific to that job</p>
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
                  <button onClick={() => deleteApplication(app.id)} className="btn-delete">🗑️ Delete</button>
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


        {/* INTERVIEW PREP TAB */}
        {activeTab === 'interview' && (
          <div className="tab-content">
            <h2>🎤 Interview Prep</h2>
            <p className="subtitle">Practice for jobs you've applied to</p>
            <div className="applications-list">
              {applications.map((app) => (
                <div key={app.id} className="application-card">
                  <div className="app-header">
                    <h4>{app.job_title}</h4>
                    <span className="app-score">Match: {app.match_score}%</span>
                  </div>
                  <p className="app-company">🏢 {app.company}</p>
                  <p className="app-date">Applied: {new Date(app.applied_at).toLocaleDateString()}</p>
                  <div className="button-row">
                    <button onClick={() => deleteApplication(app.id)} className="btn-delete">🗑️ Delete</button>
                    <button onClick={() => { setInterviewPrepJob({ title: app.job_title, company: app.company, description: app.job_title }); setShowInterviewPrep(true); }} className="btn-interview-prep">🎤 Interview Prep</button>
                  </div>
                </div>
              ))}
              {applications.length === 0 && (
                <p className="empty-state">No applications yet. Apply to jobs first!</p>
              )}
            </div>
          </div>
        )}

        {/* INTERVIEW PREP TAB */}
        {activeTab === 'interview' && (
          <div className="tab-content">
            <h2>🎤 Interview Prep</h2>
            <p className="subtitle">Practice for jobs you've applied to</p>
            <div className="applications-list">
              {applications.map((app) => (
                <div key={app.id} className="application-card">
                  <div className="app-header">
                    <h4>{app.job_title}</h4>
                    <span className="app-score">Match: {app.match_score}%</span>
                  </div>
                  <p className="app-company">🏢 {app.company}</p>
                  <p className="app-date">Applied: {new Date(app.applied_at).toLocaleDateString()}</p>
                  <div className="button-row">
                    <button onClick={() => deleteApplication(app.id)} className="btn-delete">🗑️ Delete</button>
                    <button onClick={() => { setInterviewPrepJob({ title: app.job_title, company: app.company, description: app.job_title }); setShowInterviewPrep(true); }} className="btn-interview-prep">🎤 Interview Prep</button>
                  </div>
                </div>
              ))}
              {applications.length === 0 && (
                <p className="empty-state">No applications yet. Apply to jobs first!</p>
              )}
            </div>
          </div>
        )}

        {/* Interview Prep Modal */}
        {showInterviewPrep && interviewPrepJob && (
          <InterviewPrep job={interviewPrepJob} token={token} onClose={() => { setShowInterviewPrep(false); setInterviewPrepJob(null); }} />
        )}
      </div>
    </div>
  )
}

export default Dashboard
// build: Mon May 11 16:10:16 UTC 2026
