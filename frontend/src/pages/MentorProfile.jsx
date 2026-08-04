import React, { useState, useEffect } from 'react'
import {
  User, Mail, Phone, BookOpen, Award, TrendingUp, CheckCircle,
  Clock, Edit2, Save, X, Briefcase, GraduationCap, Link,
  Users, BarChart2, Star, Linkedin, RefreshCw, Target
} from 'lucide-react'
import { apiGet, apiPut } from '../api/client'

const SPECIALIZATIONS = ['Mathematics', 'Science', 'English', 'Social Studies', 'Computer Basics']

const specColors = {
  Mathematics: 'bg-blue-100 text-blue-700 border-blue-200',
  Science: 'bg-green-100 text-green-700 border-green-200',
  English: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  'Social Studies': 'bg-orange-100 text-orange-700 border-orange-200',
  'Computer Basics': 'bg-purple-100 text-purple-700 border-purple-200',
}

const levelColors = {
  Beginner: 'bg-emerald-50 text-emerald-700',
  Intermediate: 'bg-sky-50 text-sky-700',
  Advanced: 'bg-violet-50 text-violet-700',
  Expert: 'bg-rose-50 text-rose-700',
}

export default function MentorProfile() {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [editing, setEditing] = useState(false)
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState({})
  const [saveMsg, setSaveMsg] = useState(null)

  useEffect(() => { fetchProfile() }, [])

  const fetchProfile = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiGet('/mentors/profile/me')
      setProfile(data)
      setForm({
        name: data.name || data.full_name || '',
        email: data.email || '',
        phone: data.phone || '',
        qualification: data.qualification || '',
        specialization: data.specialization || '',
        experience_years: data.experience_years || '',
        bio: data.bio || '',
        linkedin_url: data.linkedin_url || '',
      })
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const saveProfile = async () => {
    setSaving(true)
    try {
      await apiPut('/mentors/profile/me', { ...form, experience_years: form.experience_years ? parseInt(form.experience_years) : null })
      setProfile(prev => ({ ...prev, ...form, experience_years: form.experience_years ? parseInt(form.experience_years) : prev.experience_years }))
      setEditing(false)
      setSaveMsg('Profile updated successfully!')
      setTimeout(() => setSaveMsg(null), 3000)
    } catch (e) {
      alert('Failed to save profile.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <RefreshCw className="animate-spin text-primary-500 mr-3" size={24} />
        <span className="text-gray-500">Loading your profile…</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <p className="text-red-500">{error}</p>
        <button onClick={fetchProfile} className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm">Retry</button>
      </div>
    )
  }

  const displayName = profile?.name || profile?.full_name || 'Mentor'
  const stats = profile?.stats || {}
  const courses = profile?.courses || []

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      {saveMsg && (
        <div className="fixed top-20 right-6 z-50 bg-green-600 text-white px-5 py-3 rounded-xl shadow-lg flex items-center gap-2">
          <CheckCircle size={18} /> {saveMsg}
        </div>
      )}

      {/* Header Banner */}
      <div className="relative bg-gradient-to-r from-indigo-600 to-purple-500 rounded-2xl p-6 text-white overflow-hidden">
        <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(circle at 80% 50%, white 0%, transparent 60%)' }} />
        <div className="relative flex flex-col md:flex-row md:items-center gap-5">
          <div className="w-20 h-20 rounded-2xl bg-white/20 backdrop-blur border-2 border-white/40 flex items-center justify-center text-3xl font-bold text-white shrink-0">
            {displayName[0].toUpperCase()}
          </div>
          <div className="flex-1">
            <h1 className="text-2xl font-bold">{displayName}</h1>
            <p className="text-indigo-100 text-sm">{profile?.email}</p>
            <div className="flex flex-wrap items-center gap-2 mt-2">
              {profile?.specialization && (
                <span className="text-xs bg-white/20 backdrop-blur px-3 py-1 rounded-full font-medium">
                  🎓 {profile.specialization}
                </span>
              )}
              {profile?.experience_years != null && (
                <span className="text-xs bg-white/20 backdrop-blur px-3 py-1 rounded-full">
                  {profile.experience_years} yr{profile.experience_years !== 1 ? 's' : ''} experience
                </span>
              )}
              {profile?.qualification && (
                <span className="text-xs bg-white/20 backdrop-blur px-3 py-1 rounded-full">
                  {profile.qualification}
                </span>
              )}
              <span className="text-xs bg-white/20 backdrop-blur px-3 py-1 rounded-full">
                Joined {profile?.created_at ? new Date(profile.created_at).toLocaleDateString('en-IN', { month: 'long', year: 'numeric' }) : '—'}
              </span>
            </div>
          </div>
          <button
            onClick={() => setEditing(true)}
            className="flex items-center gap-2 px-4 py-2 bg-white text-indigo-700 rounded-xl font-semibold text-sm hover:bg-indigo-50 transition-colors shrink-0"
          >
            <Edit2 size={15} /> Edit Profile
          </button>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-2 gap-4">
        <StatCard icon={BookOpen} label="Courses Managed" value={stats.total_courses ?? 0} color="indigo" />
        <StatCard icon={Users} label="Total Students" value={stats.total_students ?? 0} color="purple" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left: Info */}
        <div className="md:col-span-1 space-y-4">
          {/* Contact */}
          <Section title="Contact & Identity" icon={User}>
            <InfoRow icon={Mail} label="Email" value={profile?.email} />
            {profile?.phone && <InfoRow icon={Phone} label="Phone" value={profile.phone} />}
            {profile?.linkedin_url && (
              <div className="flex items-start gap-3 py-2 border-b border-gray-50 last:border-0">
                <div className="w-7 h-7 bg-gray-50 rounded-lg flex items-center justify-center shrink-0 mt-0.5">
                  <Link size={13} className="text-gray-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-400">LinkedIn</p>
                  <a href={profile.linkedin_url} target="_blank" rel="noopener noreferrer"
                    className="text-sm font-medium text-indigo-600 hover:underline mt-0.5 block truncate max-w-[180px]">
                    View Profile
                  </a>
                </div>
              </div>
            )}
          </Section>

          {/* Professional Details */}
          <Section title="Professional Background" icon={Briefcase}>
            <InfoRow icon={GraduationCap} label="Qualification" value={profile?.qualification || '—'} />
            <div className="py-2 border-b border-gray-50 last:border-0">
              <p className="text-xs text-gray-400 mb-1.5">Specialization</p>
              {profile?.specialization ? (
                <span className={`text-xs font-semibold px-3 py-1.5 rounded-full border ${specColors[profile.specialization] || 'bg-gray-100 text-gray-600 border-gray-200'}`}>
                  {profile.specialization}
                </span>
              ) : <span className="text-sm text-gray-400">Not set</span>}
            </div>
            <InfoRow icon={Star} label="Experience" value={profile?.experience_years != null ? `${profile.experience_years} year${profile.experience_years !== 1 ? 's' : ''}` : '—'} />
          </Section>

          {/* Bio */}
          {(profile?.bio || editing) && (
            <Section title="About Me" icon={BookOpen}>
              <p className="text-sm text-gray-600 leading-relaxed">
                {profile?.bio || <span className="text-gray-400 italic">No bio added yet. Click Edit Profile to add one.</span>}
              </p>
            </Section>
          )}
        </div>

        {/* Right: Courses */}
        <div className="md:col-span-2 space-y-4">
          <Section title={`Courses Portfolio (${courses.length})`} icon={BarChart2}>
            {courses.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-6">No courses assigned yet</p>
            ) : (
              <div className="space-y-3">
                {courses.map(c => <CoursePortfolioCard key={c.course_id} course={c} />)}
              </div>
            )}
          </Section>
        </div>
      </div>

      {/* Edit Modal */}
      {editing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between px-6 py-5 border-b border-gray-100">
              <h2 className="text-xl font-bold text-gray-900">Edit Professional Profile</h2>
              <button onClick={() => setEditing(false)} className="p-2 hover:bg-gray-100 rounded-lg"><X size={20} className="text-gray-500" /></button>
            </div>
            <div className="px-6 py-5 space-y-5">
              <div className="grid grid-cols-2 gap-4">
                <Field label="Full Name" required>
                  <input type="text" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                    className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300" />
                </Field>
                <Field label="Email" required>
                  <input type="email" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                    className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300" />
                </Field>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <Field label="Phone">
                  <input type="text" value={form.phone} onChange={e => setForm(f => ({ ...f, phone: e.target.value }))}
                    className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300" />
                </Field>
                <Field label="Years of Experience">
                  <input type="number" min="0" max="50" value={form.experience_years} onChange={e => setForm(f => ({ ...f, experience_years: e.target.value }))}
                    className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300" />
                </Field>
              </div>
              <Field label="Highest Qualification">
                <input type="text" value={form.qualification} onChange={e => setForm(f => ({ ...f, qualification: e.target.value }))}
                  placeholder="e.g. B.Ed, M.Sc Mathematics, M.A. English…"
                  className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300" />
              </Field>
              <Field label="Subject Specialization">
                <select value={form.specialization} onChange={e => setForm(f => ({ ...f, specialization: e.target.value }))}
                  className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-300">
                  <option value="">Choose a subject</option>
                  {SPECIALIZATIONS.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </Field>
              <Field label="LinkedIn Profile URL">
                <input type="url" value={form.linkedin_url} onChange={e => setForm(f => ({ ...f, linkedin_url: e.target.value }))}
                  placeholder="https://linkedin.com/in/yourprofile"
                  className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300" />
              </Field>
              <Field label="Bio / About Me">
                <textarea rows={4} value={form.bio} onChange={e => setForm(f => ({ ...f, bio: e.target.value }))}
                  placeholder="Describe your teaching philosophy, experience, and what motivates you…"
                  className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 resize-none" />
              </Field>
            </div>
            <div className="flex justify-end gap-3 px-6 py-4 border-t border-gray-100">
              <button onClick={() => setEditing(false)} className="px-4 py-2 text-sm border border-gray-200 rounded-lg hover:bg-gray-50">Cancel</button>
              <button onClick={saveProfile} disabled={saving}
                className="flex items-center gap-2 px-5 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50">
                <Save size={15} />{saving ? 'Saving…' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ─── Sub-components ──────────────────────────────────────────────

const StatCard = ({ icon: Icon, label, value, color }) => {
  const schemes = {
    indigo: 'bg-indigo-50 border-indigo-100 text-indigo-700',
    purple: 'bg-purple-50 border-purple-100 text-purple-700',
  }
  return (
    <div className={`rounded-2xl border p-4 flex flex-col gap-2 ${schemes[color]}`}>
      <Icon size={20} className="opacity-70" />
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-xs font-medium opacity-70">{label}</p>
    </div>
  )
}

const Section = ({ title, icon: Icon, children }) => (
  <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden shadow-sm">
    <div className="flex items-center gap-2 px-5 py-4 border-b border-gray-50">
      <Icon size={16} className="text-indigo-500" />
      <h3 className="text-sm font-semibold text-gray-700">{title}</h3>
    </div>
    <div className="px-5 py-4">{children}</div>
  </div>
)

const InfoRow = ({ icon: Icon, label, value }) => (
  <div className="flex items-start gap-3 py-2 border-b border-gray-50 last:border-0">
    <div className="w-7 h-7 bg-gray-50 rounded-lg flex items-center justify-center shrink-0 mt-0.5">
      <Icon size={13} className="text-gray-400" />
    </div>
    <div>
      <p className="text-xs text-gray-400">{label}</p>
      <p className="text-sm font-medium text-gray-800 mt-0.5">{value || '—'}</p>
    </div>
  </div>
)

const Field = ({ label, required, children }) => (
  <div>
    <label className="block text-xs font-semibold text-gray-500 mb-1.5">
      {label}{required && <span className="text-red-400 ml-0.5">*</span>}
    </label>
    {children}
  </div>
)

const CoursePortfolioCard = ({ course }) => {
  const total = course.total_enrolled || 0
  const comp = course.completed || 0
  const prog = course.avg_progress || 0
  const compPct = total > 0 ? Math.round((comp / total) * 100) : 0

  return (
    <div className="rounded-xl border border-gray-100 bg-gray-50 px-4 py-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-gray-800">{course.course_title}</p>
          <div className="flex items-center gap-2 mt-1 flex-wrap">
            {course.track_type && (
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium border ${specColors[course.track_type] || 'bg-gray-100 text-gray-600 border-gray-200'}`}>
                {course.track_type}
              </span>
            )}
            {course.level && (
              <span className={`text-xs px-2 py-0.5 rounded-full ${levelColors[course.level] || 'bg-gray-100 text-gray-600'}`}>
                {course.level}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-3 gap-3 mt-3 pt-3 border-t border-gray-100">
        <MiniStat label="Enrolled" value={total} />
        <MiniStat label="Completed" value={comp} />
        <MiniStat label="In Progress" value={course.in_progress || 0} />
      </div>

      {/* Completion bar */}
      <div className="mt-3">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>Completion rate</span>
          <span className="font-semibold text-gray-600">{compPct}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-1.5">
          <div className="h-1.5 rounded-full bg-indigo-500 transition-all" style={{ width: `${compPct}%` }} />
        </div>
      </div>

      {prog > 0 && (
        <div className="mt-2">
          <div className="flex justify-between text-xs text-gray-400 mb-1">
            <span>Avg progress</span>
            <span className="font-semibold text-gray-600">{prog}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-1.5">
            <div className="h-1.5 rounded-full bg-purple-400 transition-all" style={{ width: `${prog}%` }} />
          </div>
        </div>
      )}
    </div>
  )
}

const MiniStat = ({ label, value }) => (
  <div className="text-center">
    <p className="text-base font-bold text-gray-800">{value}</p>
    <p className="text-xs text-gray-400">{label}</p>
  </div>
)
