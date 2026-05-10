import { useState } from 'react'
import axios from 'axios'
import './InterviewPrep.css'

const API_URL = 'http://34.207.163.174:31678/api'

function InterviewPrep({ job, token, onClose }) {
  const [prepData, setPrepData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeSection, setActiveSection] = useState('technical')

  const axiosConfig = {
    headers: { Authorization: `Bearer ${token}` }
  }

  const generatePrep = async () => {
    setLoading(true)
    try {
      const response = await axios.post(
        `${API_URL}/jobs/interview-prep`,
        {
          job_data: {
            title: job.title,
            company: job.company,
            description: job.description
          }
        },
        axiosConfig
      )

      if (response.data.status === 'success') {
        setPrepData(response.data.prep_data)
      } else {
        alert('Failed to generate interview prep')
      }
    } catch (err) {
      alert('Error: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="interview-prep-modal">
      <div className="prep-content">
        <div className="prep-header">
          <div>
            <h2>🎤 Interview Prep</h2>
            <p className="prep-subtitle">
              {job.title} at {job.company}
            </p>
          </div>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        {!prepData && (
          <div className="prep-intro">
            <div className="intro-card">
              <h3>🚀 Get Ready to Ace Your Interview!</h3>
              <p>Our AI will generate:</p>
              <ul>
                <li>✅ 10 Technical Questions specific to this role</li>
                <li>✅ 10 Behavioral Questions (STAR method)</li>
                <li>✅ 5 Company-Specific Questions</li>
                <li>✅ 5 Smart Questions to Ask the Interviewer</li>
                <li>✅ Sample Answers with Best Practices</li>
                <li>✅ Key Skills to Highlight</li>
                <li>✅ Interview Tips tailored to this role</li>
              </ul>
              <button 
                onClick={generatePrep} 
                className="btn-generate"
                disabled={loading}
              >
                {loading ? '🔄 Generating...' : '✨ Generate Interview Prep'}
              </button>
            </div>
          </div>
        )}

        {prepData && (
          <div className="prep-results">
            <div className="prep-tabs">
              <button
                className={activeSection === 'technical' ? 'prep-tab active' : 'prep-tab'}
                onClick={() => setActiveSection('technical')}
              >
                💻 Technical
              </button>
              <button
                className={activeSection === 'behavioral' ? 'prep-tab active' : 'prep-tab'}
                onClick={() => setActiveSection('behavioral')}
              >
                🎯 Behavioral
              </button>
              <button
                className={activeSection === 'company' ? 'prep-tab active' : 'prep-tab'}
                onClick={() => setActiveSection('company')}
              >
                🏢 Company
              </button>
              <button
                className={activeSection === 'tips' ? 'prep-tab active' : 'prep-tab'}
                onClick={() => setActiveSection('tips')}
              >
                💡 Tips
              </button>
            </div>

            <div className="prep-section">
              {activeSection === 'technical' && (
                <div>
                  <h3>Technical Questions</h3>
                  <div className="questions-list">
                    {prepData.technical_questions?.map((q, i) => (
                      <div key={i} className="question-card">
                        <span className="q-number">Q{i + 1}</span>
                        <p>{q}</p>
                      </div>
                    ))}
                  </div>

                  {prepData.sample_answers && (
                    <>
                      <h3 style={{ marginTop: '2rem' }}>Sample Answers</h3>
                      {prepData.sample_answers.map((sa, i) => (
                        <div key={i} className="answer-card">
                          <h4>Q: {sa.question}</h4>
                          <p className="answer">{sa.answer}</p>
                        </div>
                      ))}
                    </>
                  )}
                </div>
              )}

              {activeSection === 'behavioral' && (
                <div>
                  <h3>Behavioral Questions (Use STAR Method)</h3>
                  <div className="star-method">
                    <p><strong>STAR Method:</strong> Situation → Task → Action → Result</p>
                  </div>
                  <div className="questions-list">
                    {prepData.behavioral_questions?.map((q, i) => (
                      <div key={i} className="question-card">
                        <span className="q-number">Q{i + 1}</span>
                        <p>{q}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeSection === 'company' && (
                <div>
                  <h3>Company-Specific Questions</h3>
                  <div className="questions-list">
                    {prepData.company_questions?.map((q, i) => (
                      <div key={i} className="question-card">
                        <span className="q-number">Q{i + 1}</span>
                        <p>{q}</p>
                      </div>
                    ))}
                  </div>

                  <h3 style={{ marginTop: '2rem' }}>Questions to Ask Interviewer</h3>
                  <div className="questions-list">
                    {prepData.questions_to_ask?.map((q, i) => (
                      <div key={i} className="question-card smart">
                        <span className="q-number">💡</span>
                        <p>{q}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeSection === 'tips' && (
                <div>
                  <h3>Key Skills to Highlight</h3>
                  <div className="skills-grid">
                    {prepData.key_skills?.map((skill, i) => (
                      <div key={i} className="skill-badge">{skill}</div>
                    ))}
                  </div>

                  <h3 style={{ marginTop: '2rem' }}>Interview Tips</h3>
                  <div className="tips-list">
                    {prepData.interview_tips?.map((tip, i) => (
                      <div key={i} className="tip-card">
                        <span className="tip-icon">💡</span>
                        <p>{tip}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default InterviewPrep
