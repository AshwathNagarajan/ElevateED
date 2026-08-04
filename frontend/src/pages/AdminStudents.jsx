import React, { useState, useEffect } from 'react'
import {
  Users, Search, X, BookOpen, Calendar, Phone, User, TrendingUp, CheckCircle, Clock,
  Edit2, Trash2, AlertTriangle, Save
} from 'lucide-react'
import { apiGet, apiPut, apiDelete } from '../api/client'

const TRACKS = ['Engineering', 'Computer Science', 'Data Science', 'Business Analytics', 'Design', 'Humanities', 'Life Science', 'Commerce']

const trackColors = {
  Engineering: 'bg-cyan-100 text-cyan-700',
  'Computer Science': 'bg-blue-100 text-blue-700',
  'Data Science': 'bg-purple-100 text-purple-700',
  'Business Analytics': 'bg-green-100 text-green-700',
  Design: 'bg-yellow-100 text-yellow-700',
  Humanities: 'bg-orange-100 text-orange-700',
  'Life Science': 'bg-emerald-100 text-emerald-700',
  Commerce: 'bg-amber-100 text-amber-700',
}

const AdminStudents = () => {
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [trackFilter, setTrackFilter] = useState('')
  const [selectedStudent, setSelectedStudent] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailData, setDetailData] = useState(null)
  const [editStudent, setEditStudent] = useState(null)
  const [editForm, setEditForm] = useState({})
  const [editSaving, setEditSaving] = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState(null)
  const [deleteLoading, setDeleteLoading] = useState(false)

  useEffect(() => {
    fetchStudents()
  }, [])

  const fetchStudents = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiGet('/students/admin/list?limit=200')
      setStudents(data)
    } catch (err) {
      setError('Failed to load students. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const openStudentDetail = async (student) => {
    setSelectedStudent(student)
    setDetailData(null)
    setDetailLoading(true)
    try {
      const data = await apiGet(`/students/admin/${student.id}`)
      setDetailData(data)
    } catch (err) {
      console.warn('Failed to load student detail:', err)
    } finally {
      setDetailLoading(false)
    }
  }

  const closeDetail = () => {
    setSelectedStudent(null)
    setDetailData(null)
  }

  const openEdit = (student, e) => {
    e.stopPropagation()
    setEditForm({
      name: student.name || '',
      age: student.age || '',
      guardian_contact: student.guardian_contact || '',
      interest_track: student.interest_track || '',
      predicted_track: student.predicted_track || '',
    })
    setEditStudent(student)
    setSelectedStudent(null)
    setDetailData(null)
  }

  const saveEdit = async () => {
    if (!editStudent) return
    setEditSaving(true)
    try {
      await apiPut(`/students/admin/${editStudent.id}`, { ...editForm, age: editForm.age ? parseInt(editForm.age) : null })
      setStudents(prev => prev.map(s => s.id === editStudent.id ? { ...s, ...editForm, age: editForm.age ? parseInt(editForm.age) : s.age } : s))
      setEditStudent(null)
    } catch (err) {
      alert('Failed to save changes.')
    } finally {
      setEditSaving(false)
    }
  }

  const confirmDelete = (student, e) => {
    e.stopPropagation()
    setDeleteConfirm(student)
    setSelectedStudent(null)
    setDetailData(null)
  }

  const doDelete = async () => {
    if (!deleteConfirm) return
    setDeleteLoading(true)
    try {
      await apiDelete(`/students/admin/${deleteConfirm.id}`)
      setStudents(prev => prev.filter(s => s.id !== deleteConfirm.id))
      setDeleteConfirm(null)
    } catch (err) {
      alert('Failed to delete student.')
    } finally {
      setDeleteLoading(false)
    }
  }

  const allTracks = [...new Set(students.map(s => s.interest_track).filter(Boolean))]

  const filtered = students.filter(s => {
    const q = searchQuery.toLowerCase()
    const matchSearch = (s.name || '').toLowerCase().includes(q) ||
      (s.email || '').toLowerCase().includes(q)
    const matchTrack = !trackFilter || s.interest_track === trackFilter
    return matchSearch && matchTrack
  })

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Students</h1>
          <p className="text-gray-500">Manage and view all enrolled students</p>
        </div>
        <div className="mt-4 md:mt-0 flex items-center gap-3 bg-white border border-gray-200 rounded-xl px-5 py-3 shadow-sm">
          <Users className="text-primary-600" size={22} />
          <div>
            <p className="text-xs text-gray-500">Total Students</p>
            <p className="text-2xl font-bold text-gray-900">{students.length}</p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Search by name or email..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-300 bg-white"
          />
        </div>
        <select
          value={trackFilter}
          onChange={e => setTrackFilter(e.target.value)}
          className="px-4 py-2.5 border border-gray-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-primary-300 text-sm text-gray-700"
        >
          <option value="">All Tracks</option>
          {allTracks.map(t => <option key={t} value={t}>{t}</option>)}
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
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Student</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Email</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Age</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Track</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Enrollments</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Joined</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              [...Array(6)].map((_, i) => (
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
                  <Users size={40} className="mx-auto mb-3 opacity-30" />
                  <p>No students found</p>
                </td>
              </tr>
            ) : (
              filtered.map((student, idx) => (
                <tr
                  key={student.id}
                  onClick={() => openStudentDetail(student)}
                  className="border-b border-gray-100 hover:bg-primary-50 cursor-pointer transition-colors"
                >
                  <td className="px-5 py-4 text-sm text-gray-400">{idx + 1}</td>
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-semibold text-sm">
                        {(student.name || '?')[0].toUpperCase()}
                      </div>
                      <span className="font-medium text-gray-900">{student.name}</span>
                    </div>
                  </td>
                  <td className="px-5 py-4 text-sm text-gray-500">{student.email || '—'}</td>
                  <td className="px-5 py-4 text-sm text-gray-700">{student.age || '—'}</td>
                  <td className="px-5 py-4">
                    {student.interest_track ? (
                      <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${trackColors[student.interest_track] || 'bg-gray-100 text-gray-600'}`}>
                        {student.interest_track}
                      </span>
                    ) : <span className="text-gray-400 text-sm">—</span>}
                  </td>
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-1.5 text-sm font-medium text-gray-700">
                      <BookOpen size={14} className="text-primary-500" />
                      {student.enrollment_count ?? 0}
                    </div>
                  </td>
                  <td className="px-5 py-4 text-sm text-gray-400">
                    {student.created_at ? new Date(student.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : '—'}
                  </td>
                  <td className="px-5 py-4" onClick={e => e.stopPropagation()}>
                    <div className="flex items-center gap-1">
                      <button onClick={e => openEdit(student, e)} className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors" title="Edit"><Edit2 size={15} /></button>
                      <button onClick={e => confirmDelete(student, e)} className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors" title="Delete"><Trash2 size={15} /></button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Total count */}
      {!loading && (
        <p className="text-sm text-gray-400 mt-3 text-right">
          Showing {filtered.length} of {students.length} students
        </p>
      )}

      {/* Info Card Modal */}
      {/* Edit Modal */}
      {editStudent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
            <div className="flex items-center justify-between px-6 py-5 border-b border-gray-100">
              <h2 className="text-xl font-bold text-gray-900">Edit Student</h2>
              <button onClick={() => setEditStudent(null)} className="p-2 hover:bg-gray-100 rounded-lg"><X size={20} className="text-gray-500" /></button>
            </div>
            <div className="px-6 py-5 space-y-4">
              {[['name','Name','text'],['age','Age','number'],['guardian_contact','Guardian Contact','text']].map(([key, label, type]) => (
                <div key={key}>
                  <label className="block text-xs font-medium text-gray-500 mb-1">{label}</label>
                  <input type={type} value={editForm[key]} onChange={e => setEditForm(f => ({...f,[key]:e.target.value}))} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-300" />
                </div>
              ))}
              {[['interest_track','Interest Track'],['predicted_track','Predicted Track']].map(([key, label]) => (
                <div key={key}>
                  <label className="block text-xs font-medium text-gray-500 mb-1">{label}</label>
                  <select value={editForm[key]} onChange={e => setEditForm(f => ({...f,[key]:e.target.value}))} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-300 bg-white">
                    <option value="">Select track</option>
                    {TRACKS.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
              ))}
            </div>
            <div className="flex justify-end gap-3 px-6 py-4 border-t border-gray-100">
              <button onClick={() => setEditStudent(null)} className="px-4 py-2 text-sm border border-gray-200 rounded-lg hover:bg-gray-50">Cancel</button>
              <button onClick={saveEdit} disabled={editSaving} className="flex items-center gap-2 px-4 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50">
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
              <h2 className="text-xl font-bold text-gray-900 mb-2">Delete Student?</h2>
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

      {selectedStudent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-5 border-b border-gray-100">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-bold text-xl">
                  {(selectedStudent.name || '?')[0].toUpperCase()}
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{selectedStudent.name}</h2>
                  <p className="text-sm text-gray-500">{selectedStudent.email || 'No email'}</p>
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
              {/* Basic Info */}
              <div className="grid grid-cols-2 gap-4">
                <InfoItem icon={User} label="Age" value={selectedStudent.age ? `${selectedStudent.age} years` : '—'} />
                <InfoItem icon={Phone} label="Guardian Contact" value={selectedStudent.guardian_contact || '—'} />
                <InfoItem icon={TrendingUp} label="Interest Track" value={selectedStudent.interest_track || '—'} colored={trackColors[selectedStudent.interest_track]} />
                <InfoItem icon={TrendingUp} label="Predicted Track" value={selectedStudent.predicted_track || '—'} />
                <InfoItem icon={Calendar} label="Member Since" value={selectedStudent.created_at ? new Date(selectedStudent.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' }) : '—'} />
                <InfoItem icon={BookOpen} label="Enrolled Courses" value={String(selectedStudent.enrollment_count ?? 0)} />
              </div>

              {/* Enrollments */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                  <BookOpen size={15} className="text-primary-500" />
                  Course Enrollments
                </h3>

                {detailLoading ? (
                  <div className="space-y-2">
                    {[1, 2].map(i => (
                      <div key={i} className="h-14 bg-gray-100 rounded-xl animate-pulse" />
                    ))}
                  </div>
                ) : detailData?.enrollments?.length > 0 ? (
                  <div className="space-y-2">
                    {detailData.enrollments.map((enr, i) => (
                      <div key={i} className="flex items-center justify-between bg-gray-50 rounded-xl px-4 py-3">
                        <div>
                          <p className="text-sm font-medium text-gray-800">{enr.course_title}</p>
                          <p className="text-xs text-gray-400 mt-0.5">
                            Enrolled: {enr.enrolled_at ? new Date(enr.enrolled_at).toLocaleDateString('en-IN') : '—'}
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="flex items-center gap-1.5">
                            {enr.completed ? (
                              <span className="flex items-center gap-1 text-xs text-green-600 font-medium bg-green-50 px-2 py-0.5 rounded-full">
                                <CheckCircle size={12} /> Completed
                              </span>
                            ) : (
                              <span className="flex items-center gap-1 text-xs text-blue-600 font-medium bg-blue-50 px-2 py-0.5 rounded-full">
                                <Clock size={12} /> {Math.round(enr.progress_percentage)}%
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400 text-center py-4">Not enrolled in any courses yet</p>
                )}
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

export default AdminStudents
