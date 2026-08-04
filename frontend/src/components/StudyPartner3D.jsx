import React, { useEffect, useMemo, useState } from 'react'
import { Award, Sparkles, X } from 'lucide-react'
import { apiGet } from '../api/client'

const messages = [
  'I am tracking your learning signals. One calm note at a time.',
  'Read the example, try the quiz, and I will help adjust the next step.',
  'Harder topics become smaller when you finish one clear step.',
  'Your rewards grow from real effort: notes read, quizzes tried, lessons completed.',
]

const StudyPartner3D = ({ userRole }) => {
  const [hidden, setHidden] = useState(false)
  const [achievements, setAchievements] = useState(null)
  const [guidance, setGuidance] = useState(null)
  const [messageIndex, setMessageIndex] = useState(0)

  const fetchPartnerState = async () => {
    if (userRole !== 'student') return
    try {
      const [achievementData, guidanceData] = await Promise.all([
        apiGet('/badges/my-achievements').catch(() => null),
        apiGet('/recommendations/guidance-plan').catch(() => null),
      ])
      setAchievements(achievementData)
      setGuidance(guidanceData)
    } catch {
      // Partner stays motivational even if a dashboard endpoint is unavailable.
    }
  }

  useEffect(() => {
    fetchPartnerState()
    const onProgress = () => fetchPartnerState()
    window.addEventListener('learning-progress-updated', onProgress)
    return () => window.removeEventListener('learning-progress-updated', onProgress)
  }, [userRole])

  useEffect(() => {
    const id = window.setInterval(() => {
      setMessageIndex(index => (index + 1) % messages.length)
    }, 9000)
    return () => window.clearInterval(id)
  }, [])

  const partnerMessage = useMemo(() => {
    const nextStep = guidance?.next_steps?.[0]?.title
    if (nextStep) return `Next focus: ${nextStep}. I am with you.`
    return messages[messageIndex]
  }, [guidance, messageIndex])

  if (userRole !== 'student' || hidden) return null

  return (
    <aside className="fixed bottom-4 right-4 z-40 w-[min(92vw,320px)]">
      <div className="rounded-lg border border-white/15 bg-slate-950/88 p-4 text-white shadow-2xl shadow-black/40 backdrop-blur-xl">
        <div className="mb-3 flex items-start justify-between gap-3">
          <div>
            <div className="mb-1 flex items-center gap-2">
              <Sparkles size={16} className="text-cyan-200" />
              <p className="text-sm font-black">Nova, your study partner</p>
            </div>
            <p className="text-xs leading-5 text-slate-300">{partnerMessage}</p>
          </div>
          <button
            type="button"
            onClick={() => setHidden(true)}
            className="rounded-lg p-1 text-slate-400 hover:bg-white/10 hover:text-white"
            aria-label="Hide study partner"
          >
            <X size={16} />
          </button>
        </div>

        <div className="mb-3 flex items-center justify-between rounded-lg border border-white/10 bg-white/8 px-3 py-2">
          <div className="flex items-center gap-2">
            <Award size={16} className="text-amber-200" />
            <span className="text-xs font-bold text-slate-200">Rewards</span>
          </div>
          <span className="text-sm font-black text-amber-100">
            {achievements?.total_points || 0} pts
          </span>
        </div>

        <div className="nova-stage" aria-hidden="true">
          <div className="nova-shadow" />
          <div className="nova-character">
            <div className="nova-head">
              <span className="nova-eye nova-eye-left" />
              <span className="nova-eye nova-eye-right" />
              <span className="nova-smile" />
            </div>
            <div className="nova-core">
              <span className="nova-badge">{achievements?.total_badges || 0}</span>
            </div>
            <div className="nova-arm nova-arm-left" />
            <div className="nova-arm nova-arm-right" />
            <div className="nova-orbit nova-orbit-one" />
            <div className="nova-orbit nova-orbit-two" />
          </div>
        </div>
      </div>
    </aside>
  )
}

export default StudyPartner3D
