import React, { useState, useEffect } from 'react'
import {
  GraduationCap, Search, X, BookOpen, Calendar,
  Phone, Linkedin, Award, Briefcase, Star,
  Edit2, Trash2, AlertTriangle, Save
} from 'lucide-react'
import { apiGet, apiPut, apiDelete } from '../api/client'

const TRACKS = ['Mathematics', 'Science', 'English', 'Social Studies', 'Computer Basics']


const specializationColors = [
  'bg-blue-100 text-blue-700',
  'bg-purple-100 text-purple-700',
  'bg-green-100 text-green-700',
  'bg-orange-100 text-orange-700',
  'bg-pink-100 text-pink-700',
  'bg-teal-100 text-teal-700',
]

const AdminMentors = () => {
  const [mentors, setMentors] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [specFilter, setSpecFilter] = useState('')
  const [selectedMentor, setSelectedMentor] = useState(null)
  const [editMentor, setEditMentor] = useState(null)
  const [editForm, setEditForm] = useState({})
  const [editSaving, setEditSaving] = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState(null)
  const [deleteLoading, setDeleteLoading] = useState(false)

  useEffect(() => {
    fetchMentors()
  }, [])

  const fetchMentors = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiGet('/mentors/admin/list?limit=200')
      setMentors(data)
    } catch (err) {
      setError('Failed to load mentors. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const closeDetail = () => setSelectedMentor(null)

  const openEdit = (mentor, e) => {
    e.stopPropagation()
    setEditForm({
      name: mentor.name || '',
      phone: mentor.phone || '',
      qualification: mentor.qualification || '',
      specialization: mentor.specialization || '',
      experience_years: mentor.experience_years ?? '',
      bio: mentor.bio || '',
      linkedin_url: mentor.linkedin_url || '',
    })
    setEditMentor(mentor)
    setSelectedMentor(null)
  }

  const saveEdit = async () => {
    if (!editMentor) return
    setEditSaving(true)
    try {
      await apiPut(`/mentors/admin/${editMentor.id}`, { ...editForm, experience_years: editForm.experience_years ? parseInt(editForm.experience_years) : null })
      setMentors(prev => prev.map(m => m.id === editMentor.id ? { ...m, ...editForm, experience_years: editForm.experience_years ? parseInt(editForm.experience_years) : m.experience_years } : m))
      setEditMentor(null)
    } catch (err) {
      alert('Failed to save changes.')
    } finally {
      setEditSaving(false)
    }
  }

  const confirmDelete = (mentor, e) => {
    e.stopPropagation()
    setDeleteConfirm(mentor)
    setSelectedMentor(null)
  }

  const doDelete = async () => {
    if (!deleteConfirm) return
    setDeleteLoading(true)
    try {
      await apiDelete(`/mentors/admin/${deleteConfirm.id}`)
      setDeleteConfirm(null)
      fetchMentors()
    } catch (err) {
      alert('Failed to delete mentor.')
    } finally {
      setDeleteLoading(false)
    }
  }

  const allSpecs = [...new Set(mentors.map(m => m.specialization).filter(Boolean))]

  const filtered = mentors.filter(m => {
    const q = searchQuery.toLowerCase()
    const matchSearch = (m.name || '').toLowerCase().includes(q) ||
      (m.email || '').toLowerCase().includes(q) ||
      (m.specialization || '').toLowerCase().includes(q)
    const matchSpec = !specFilter || m.specialization === specFilter
    return matchSearch && matchSpec
  })

  const getSpecColor = (spec) => {
    if (!spec) return 'bg-gray-100 text-gray-600'
    const idx = allSpecs.indexOf(spec) % specializationColors.length
    return specializationColors[idx >= 0 ? idx : 0]
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Mentors</h1>
          <p className="text-gray-500">View and manage all registered mentors</p>
        </div>
        <div className="mt-4 md:mt-0 flex items-center gap-3 bg-white border border-gray-200 rounded-xl px-5 py-3 shadow-sm">
          <GraduationCap className="text-purple-600" size={22} />
          <div>
            <p className="text-xs text-gray-500">Total Mentors</p>
            <p className="text-2xl font-bold text-gray-900">{mentors.length}</p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Search by name, email, or specialization..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-300 bg-white"
          />
        </div>
        <select
          value={specFilter}
          onChange={e => setSpecFilter(e.target.value)}
          className="px-4 py-2.5 border border-gray-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-primary-300 text-sm text-gray-700"
        >
          <option value="">All Specializations</option>
          {allSpecs.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-3 bg-red-50 border border-red-200 rounded-xl p-4 mb-6 text-red-700">
          <X size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Table */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">#</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Mentor</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Email</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Specialization</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Qualification</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Experience</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Courses</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              [...Array(4)].map((_, i) => (
                <tr key={i} className="border-b border-gray-100">
                  {[...Array(7)].map((_, j) => (
                    <td key={j} className="px-5 py-4">
                      <div className="h-4 bg-gray-100 rounded animate-pulse" />
                    </td>
                  ))}
                </tr>
              ))
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-16 text-gray-400">
                  <GraduationCap size={40} className="mx-auto mb-3 opacity-30" />
                  <p>No mentors found</p>
                </td>
              </tr>
            ) : (
              filtered.map((mentor, idx) => (
                <tr
                  key={mentor.id}
                  onClick={() => setSelectedMentor(mentor)}
                  className="border-b border-gray-100 hover:bg-purple-50 cursor-pointer transition-colors"
                >
                  <td className="px-5 py-4 text-sm text-gray-400">{idx + 1}</td>
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-purple-100 flex items-center justify-center text-purple-700 font-semibold text-sm">
                        {(mentor.name || '?')[0].toUpperCase()}
                      </div>
                      <span className="font-medium text-gray-900">{mentor.name}</span>
                    </div>
                  </td>
                  <td className="px-5 py-4 text-sm text-gray-500">{mentor.email || '—'}</td>
                  <td className="px-5 py-4">
                    {mentor.specialization ? (
                      <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${getSpecColor(mentor.specialization)}`}>
                        {mentor.specialization}
                      </span>
                    ) : <span className="text-gray-400 text-sm">—</span>}
                  </td>
                  <td className="px-5 py-4 text-sm text-gray-700">{mentor.qualification || '—'}</td>
                  <td className="px-5 py-4">
                    {mentor.experience_years != null ? (
                      <div className="flex items-center gap-1.5 text-sm text-gray-700">
                        <Star size={13} className="text-yellow-500" />
                        {mentor.experience_years} yr{mentor.experience_years !== 1 ? 's' : ''}
                      </div>
                    ) : <span className="text-gray-400 text-sm">—</span>}
                  </td>
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-1.5 text-sm font-medium text-gray-700">
                      <BookOpen size={14} className="text-purple-500" />
                      {mentor.course_count ?? 0}
                    </div>
                  </td>
                  <td className="px-5 py-4" onClick={e => e.stopPropagation()}>
                    <div className="flex items-center gap-1">
                      <button onClick={e => openEdit(mentor, e)} className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors" title="Edit"><Edit2 size={15} /></button>
                      <button onClick={e => confirmDelete(mentor, e)} className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors" title="Delete"><Trash2 size={15} /></button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {!loading && (
        <p className="text-sm text-gray-400 mt-3 text-right">
          Showing {filtered.length} of {mentors.length} mentors
        </p>
      )}

      {/* Info Card Modal */}
      {selectedMentor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-5 border-b border-gray-100">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-full bg-purple-100 flex items-center justify-center text-purple-700 font-bold text-xl">
                  {(selectedMentor.name || '?')[0].toUpperCase()}
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{selectedMentor.name}</h2>
                  <p className="text-sm text-gray-500">{selectedMentor.email || 'No email'}</p>
                </div>
              </div>
              <button
                onClick={closeDetail}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X size={20} className="text-gray-500" />
              </button>
            </div>

            <div className="px-6 py-5 space-y-5">
              {/* Stats row */}
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-purple-50 rounded-xl px-4 py-3 text-center">
                  <p className="text-3xl font-bold text-purple-700">{selectedMentor.course_count ?? 0}</p>
                  <p className="text-xs text-gray-500 mt-1">Courses Taught</p>
                </div>
                <div className="bg-yellow-50 rounded-xl px-4 py-3 text-center">
                  <p className="text-3xl font-bold text-yellow-700">{selectedMentor.experience_years ?? 0}</p>
                  <p className="text-xs text-gray-500 mt-1">Years Experience</p>
                </div>
              </div>

              {/* Details grid */}
              <div className="grid grid-cols-2 gap-3">
                <InfoItem icon={Award} label="Qualification" value={selectedMentor.qualification || '—'} />
                <InfoItem icon={Briefcase} label="Specialization" value={selectedMentor.specialization || '—'} colored={getSpecColor(selectedMentor.specialization)} />
                <InfoItem icon={Phone} label="Phone" value={selectedMentor.phone || '—'} />
                <InfoItem icon={Calendar} label="Member Since" value={selectedMentor.created_at ? new Date(selectedMentor.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' }) : '—'} />
              </div>

              {/* Bio */}
              {selectedMentor.bio && (
                <div className="bg-gray-50 rounded-xl px-4 py-4">
                  <p className="text-xs text-gray-400 mb-2 font-medium uppercase tracking-wider">About</p>
                  <p className="text-sm text-gray-700 leading-relaxed">{selectedMentor.bio}</p>
                </div>
              )}

              {/* LinkedIn */}
              {selectedMentor.linkedin_url && (
                <a
                  href={selectedMentor.linkedin_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
                  onClick={e => e.stopPropagation()}
                >
                  <Linkedin size={16} />
                  View LinkedIn Profile
                </a>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {editMentor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between px-6 py-5 border-b border-gray-100">
              <h2 className="text-xl font-bold text-gray-900">Edit Mentor</h2>
              <button onClick={() => setEditMentor(null)} className="p-2 hover:bg-gray-100 rounded-lg"><X size={20} className="text-gray-500" /></button>
            </div>
            <div className="px-6 py-5 space-y-4">
              {[['name','Name','text'],['phone','Phone','text'],['qualification','Qualification','text'],['experience_years','Experience (years)','number'],['linkedin_url','LinkedIn URL','text']].map(([key, label, type]) => (
                <div key={key}>
                  <label className="block text-xs font-medium text-gray-500 mb-1">{label}</label>
                  <input type={type} value={editForm[key]} onChange={e => setEditForm(f => ({...f,[key]:e.target.value}))} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-300" />
                </div>
              ))}
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Specialization</label>
                <select value={editForm.specialization} onChange={e => setEditForm(f => ({...f, specialization: e.target.value}))} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-300 bg-white">
                  <option value="">Select subject</option>
                  {TRACKS.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Bio</label>
                <textarea value={editForm.bio} onChange={e => setEditForm(f => ({...f, bio: e.target.value}))} rows={3} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-300 resize-none" />
              </div>
            </div>
            <div className="flex justify-end gap-3 px-6 py-4 border-t border-gray-100">
              <button onClick={() => setEditMentor(null)} className="px-4 py-2 text-sm border border-gray-200 rounded-lg hover:bg-gray-50">Cancel</button>
              <button onClick={saveEdit} disabled={editSaving} className="flex items-center gap-2 px-4 py-2 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50">
                <Save size={15} />{editSaving ? 'Saving…' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirm Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm">
            <div className="flex flex-col items-center px-6 py-8 text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
                <AlertTriangle className="text-red-500" size={28} />
              </div>
              <h2 className="text-xl font-bold text-gray-900 mb-2">Delete Mentor?</h2>
              <p className="text-sm text-gray-500 mb-6">This will permanently delete <strong>{deleteConfirm.name}</strong> and all their data. This cannot be undone.</p>
              <div className="flex gap-3 w-full">
                <button onClick={() => setDeleteConfirm(null)} className="flex-1 px-4 py-2 border border-gray-200 rounded-lg text-sm hover:bg-gray-50">Cancel</button>
                <button onClick={doDelete} disabled={deleteLoading} className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 disabled:opacity-50">
                  {deleteLoading ? 'Deleting…' : 'Delete'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

const InfoItem = ({ icon: Icon, label, value, colored }) => (
  <div className="bg-gray-50 rounded-xl px-4 py-3">
    <p className="text-xs text-gray-400 mb-1 flex items-center gap-1.5">
      <Icon size={12} /> {label}
    </p>
    {colored ? (
      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${colored}`}>{value}</span>
    ) : (
      <p className="text-sm font-semibold text-gray-800 truncate">{value}</p>
    )}
  </div>
)

export default AdminMentors
