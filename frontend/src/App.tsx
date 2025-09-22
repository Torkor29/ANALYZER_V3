import React, { useMemo, useRef, useState } from 'react'
import axios from 'axios'
import { Line, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend)

type AnalyzeResponse = { success: boolean; task_id?: string; error?: string }
type StatusResponse = {
  success?: boolean
  progress: number
  message: string
  error?: string | null
  report_url?: string
  statistics?: any
}

export const App: React.FC = () => {
  const [files, setFiles] = useState<File[]>([])
  const [isDragOver, setIsDragOver] = useState<boolean>(false)
  const [solde, setSolde] = useState<string>('10000')
  const [filter, setFilter] = useState<'tous' | 'forex' | 'autres'>('tous')
  const [taskId, setTaskId] = useState<string | null>(null)
  const [status, setStatus] = useState<StatusResponse | null>(null)
  const [uiError, setUiError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState<boolean>(false)
  const [pairs, setPairs] = useState<string[]>([])
  const [selectedPairs, setSelectedPairs] = useState<Set<string>>(new Set())
  const [dateStart, setDateStart] = useState<string>('')
  const [dateEnd, setDateEnd] = useState<string>('')
  const [multiplier, setMultiplier] = useState<string>('1')
  const pollingRef = useRef<number | null>(null)

  // Pré-calculs graphiques pour éviter les IIFE dans le JSX
  const hoursLabels = useMemo(() => Array.from({ length: 24 }, (_, i) => `${i}h`), [])
  const dayLabels = useMemo(() => ['Lun','Mar','Mer','Jeu','Ven','Sam','Dim'], [])
  const monthLabels = useMemo(() => ['Jan','Fév','Mar','Avr','Mai','Juin','Juil','Aoû','Sep','Oct','Nov','Déc'], [])

  function Section({ title, icon, defaultOpen = false, children }: { title: string; icon: string; defaultOpen?: boolean; children: React.ReactNode }) {
    return (
      <details open={defaultOpen} style={{ border: '2px solid #e8ebff', borderRadius: 10, margin: '14px 0', overflow: 'hidden', background: '#fff' }}>
        <summary style={{ listStyle: 'none', cursor: 'pointer', background: '#f8f9ff', padding: '12px 16px', display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ color: '#667eea' }}><i className={icon} /></span>
          <span style={{ color: '#333', fontWeight: 600 }}>{title}</span>
          <span style={{ marginLeft: 'auto', color: '#667eea', fontWeight: 700 }}>▼</span>
        </summary>
        <div style={{ padding: 14 }}>{children}</div>
      </details>
    )
  }

  // Garantit un schéma valide pour react-chartjs-2
  function ensureDatasets(data: any) {
    const safe = data ?? { labels: [], datasets: [] }
    if (!Array.isArray((safe as any).datasets)) {
      ;(safe as any).datasets = []
    }
    return safe
  }

  function SafeBar({ data, options }: { data: any, options?: any }) {
    let d = ensureDatasets(typeof data === 'function' ? data() : data)
    const labels = Array.isArray((d as any).labels) ? (d as any).labels : []
    const datasets = Array.isArray((d as any).datasets) ? (d as any).datasets : []
    ;(d as any).labels = labels
    ;(d as any).datasets = datasets
      .filter((ds: any) => ds && typeof ds === 'object')
      .map((ds: any) => ({
        label: String(ds.label ?? ''),
        data: Array.isArray(ds.data) ? ds.data : [],
        backgroundColor: ds.backgroundColor ?? 'rgba(0,0,0,0.1)',
        borderColor: ds.borderColor ?? 'rgba(0,0,0,0.1)',
        borderWidth: ds.borderWidth ?? 1
      }))
    if (!d.datasets || d.datasets.length === 0) return null
    return <Bar data={d as any} options={options} />
  }

  function SafeLine({ data, options }: { data: any, options?: any }) {
    let d = ensureDatasets(typeof data === 'function' ? data() : data)
    const labels = Array.isArray((d as any).labels) ? (d as any).labels : []
    const datasets = Array.isArray((d as any).datasets) ? (d as any).datasets : []
    ;(d as any).labels = labels
    ;(d as any).datasets = datasets
      .filter((ds: any) => ds && typeof ds === 'object')
      .map((ds: any) => ({
        label: String(ds.label ?? ''),
        data: Array.isArray(ds.data) ? ds.data : [],
        backgroundColor: ds.backgroundColor ?? 'rgba(0,0,0,0.1)',
        borderColor: ds.borderColor ?? 'rgba(0,0,0,0.4)',
        borderWidth: ds.borderWidth ?? 2,
        tension: ds.tension ?? 0.1,
        fill: ds.fill ?? true
      }))
    if (!d.datasets || d.datasets.length === 0) return null
    return <Line data={d as any} options={options} />
  }

  function buildEmptyStatistics(from: any): any {
    const base = from || {}
    return {
      ...base,
      total_trades: 0,
      profit_total: 0,
      profit_compose: 0,
      pips_totaux: 0,
      solde_final: base.solde_final ?? 0,
      rendement_pct: 0,
      trades_gagnants: 0,
      trades_perdants: 0,
      taux_reussite: 0,
      drawdown_max: 0,
      heures_in_counts: {},
      heures_out_counts: {},
      profits_par_heure_out: {},
      profits_par_jour_out: {},
      profits_par_mois_out: {},
      profits_pos_par_heure_out: {},
      pertes_abs_par_heure_out: {},
      profits_pos_par_jour_out: {},
      pertes_abs_par_jour_out: {},
      profits_pos_par_mois_out: {},
      pertes_abs_par_mois_out: {},
      tp_par_heure: {},
      sl_par_heure: {},
      tp_par_jour: {},
      sl_par_jour: {},
      tp_par_mois: {},
      sl_par_mois: {},
      duree_moyenne_minutes: null,
      duree_mediane_minutes: null,
      evolution_somme_cumulee: [],
    }
  }

  const chartInData = useMemo(() => {
    const src = status?.statistics?.heures_in_counts || {}
    return status?.statistics ? { labels: hoursLabels, datasets: [{ label: 'IN (comptage)', data: hoursLabels.map((_, i) => src?.[i] ?? 0), backgroundColor: 'rgba(102,126,234,0.7)' }] } : null
  }, [status?.statistics?.heures_in_counts, status?.statistics, hoursLabels])

  const chartOutData = useMemo(() => {
    const src = status?.statistics?.heures_out_counts || {}
    return status?.statistics ? { labels: hoursLabels, datasets: [{ label: 'OUT (dernier) (comptage)', data: hoursLabels.map((_, i) => src?.[i] ?? 0), backgroundColor: 'rgba(86,171,47,0.7)' }] } : null
  }, [status?.statistics?.heures_out_counts, status?.statistics, hoursLabels])

  const chartPLHourData = useMemo(() => {
    if (!status?.statistics) return null
    const pos = status.statistics?.profits_pos_par_heure_out || {}
    const neg = status.statistics?.pertes_abs_par_heure_out || status.statistics?.pertes_par_heure_out || {}
    return { labels: hoursLabels, datasets: [
      { label: 'Profits (≥0)', data: hoursLabels.map((_, i) => pos?.[i] ?? 0), backgroundColor: 'rgba(86,171,47,0.7)' },
      { label: 'Pertes (≤0)', data: hoursLabels.map((_, i) => neg?.[i] ?? 0), backgroundColor: 'rgba(229,62,62,0.7)' }
    ] }
  }, [status?.statistics?.profits_pos_par_heure_out, status?.statistics?.pertes_abs_par_heure_out, status?.statistics?.pertes_par_heure_out, status?.statistics, hoursLabels])

  const chartPLDayData = useMemo(() => {
    if (!status?.statistics) return null
    const pos = status.statistics?.profits_pos_par_jour_out || {}
    const neg = status.statistics?.pertes_abs_par_jour_out || status.statistics?.pertes_par_jour_out || {}
    return { labels: dayLabels, datasets: [
      { label: 'Profits (≥0)', data: dayLabels.map((_, i) => pos?.[i] ?? 0), backgroundColor: 'rgba(86,171,47,0.7)' },
      { label: 'Pertes (≤0)', data: dayLabels.map((_, i) => neg?.[i] ?? 0), backgroundColor: 'rgba(229,62,62,0.7)' }
    ] }
  }, [status?.statistics?.profits_pos_par_jour_out, status?.statistics?.pertes_abs_par_jour_out, status?.statistics?.pertes_par_jour_out, status?.statistics, dayLabels])

  const chartPLMonthData = useMemo(() => {
    if (!status?.statistics) return null
    const pos = status.statistics?.profits_pos_par_mois_out || {}
    const neg = status.statistics?.pertes_abs_par_mois_out || status.statistics?.pertes_par_mois_out || {}
    return { labels: monthLabels, datasets: [
      { label: 'Profits (≥0)', data: monthLabels.map((_, i) => pos?.[i+1] ?? 0), backgroundColor: 'rgba(86,171,47,0.7)' },
      { label: 'Pertes (≤0)', data: monthLabels.map((_, i) => neg?.[i+1] ?? 0), backgroundColor: 'rgba(229,62,62,0.7)' }
    ] }
  }, [status?.statistics?.profits_pos_par_mois_out, status?.statistics?.pertes_abs_par_mois_out, status?.statistics?.pertes_par_mois_out, status?.statistics, monthLabels])

  const chartTPHourData = useMemo(() => {
    if (!status?.statistics) return null
    const tp = status.statistics?.tp_par_heure || {}
    const sl = status.statistics?.sl_par_heure || {}
    return { labels: hoursLabels, datasets: [
      { label: 'TP (nb)', data: hoursLabels.map((_, i) => tp?.[i] ?? 0), backgroundColor: 'rgba(86,171,47,0.7)' },
      { label: 'SL (nb)', data: hoursLabels.map((_, i) => sl?.[i] ?? 0), backgroundColor: 'rgba(229,62,62,0.7)' }
    ] }
  }, [status?.statistics?.tp_par_heure, status?.statistics?.sl_par_heure, status?.statistics, hoursLabels])

  const chartTPDayData = useMemo(() => {
    if (!status?.statistics) return null
    const tp = status.statistics?.tp_par_jour || {}
    const sl = status.statistics?.sl_par_jour || {}
    return { labels: dayLabels, datasets: [
      { label: 'TP (nb)', data: dayLabels.map((_, i) => tp?.[i] ?? 0), backgroundColor: 'rgba(86,171,47,0.7)' },
      { label: 'SL (nb)', data: dayLabels.map((_, i) => sl?.[i] ?? 0), backgroundColor: 'rgba(229,62,62,0.7)' }
    ] }
  }, [status?.statistics?.tp_par_jour, status?.statistics?.sl_par_jour, status?.statistics, dayLabels])

  const chartTPMonthData = useMemo(() => {
    if (!status?.statistics) return null
    const tp = status.statistics?.tp_par_mois || {}
    const sl = status.statistics?.sl_par_mois || {}
    return { labels: monthLabels, datasets: [
      { label: 'TP (nb)', data: monthLabels.map((_, i) => tp?.[i+1] ?? 0), backgroundColor: 'rgba(86,171,47,0.7)' },
      { label: 'SL (nb)', data: monthLabels.map((_, i) => sl?.[i+1] ?? 0), backgroundColor: 'rgba(229,62,62,0.7)' }
    ] }
  }, [status?.statistics?.tp_par_mois, status?.statistics?.sl_par_mois, status?.statistics, monthLabels])

  const canAnalyze = useMemo(() => files.length > 0, [files])

  function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (!e.target.files) return
    setFiles(Array.from(e.target.files))
  }

  function onDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)
    if (e.dataTransfer?.files?.length) {
      const dropped = Array.from(e.dataTransfer.files).filter(f => /\.xlsx$|\.xls$/i.test(f.name))
      setFiles(prev => {
        const names = new Set(prev.map(f => f.name))
        return [...prev, ...dropped.filter(f => !names.has(f.name))]
      })
    }
  }

  function onDragOver(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(true)
  }

  function onDragLeave() {
    setIsDragOver(false)
  }

  async function startAnalyze() {
    if (files.length === 0) {
      setUiError('Veuillez sélectionner au moins un fichier Excel (.xls, .xlsx).')
      return
    }
    setUiError(null)
    setSubmitting(true)
    const form = new FormData()
    files.forEach(f => form.append('files', f))
    form.append('filter_type', filter)
    form.append('solde_initial', solde)
    form.append('multiplier', multiplier)
    try {
      const { data } = await axios.post<AnalyzeResponse>('/api/analyze', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      if (!data.success || !data.task_id) {
        setUiError(data.error || "Erreur inconnue lors du démarrage de l'analyse")
        setStatus({ progress: 100, message: 'Erreur', error: data.error || 'Erreur inconnue' })
        setSubmitting(false)
        return
      }
      setTaskId(data.task_id)
      setStatus({ progress: 0, message: 'Démarré' })
      if (pollingRef.current) window.clearInterval(pollingRef.current)
      pollingRef.current = window.setInterval(async () => {
        try {
          const { data: st } = await axios.get<StatusResponse>(`/api/status/${data.task_id}`)
          setStatus(st as any)
          const newPairs = (st as any)?.statistics?.pairs || []
          if (Array.isArray(newPairs)) {
            setPairs(newPairs)
            setSelectedPairs(new Set(newPairs))
          }
          if ((st as any).progress >= 100) {
            if (pollingRef.current) window.clearInterval(pollingRef.current)
            setSubmitting(false)
          }
        } catch (e: any) {
          setUiError('Erreur réseau pendant le suivi de progression')
          setSubmitting(false)
        }
      }, 1200)
    } catch (e: any) {
      const status = e?.response?.status
      const url = e?.config?.url || '/api/analyze'
      const msg = status ? `HTTP ${status} sur ${url}` : (e?.message || "Erreur réseau lors de l'envoi")
      setUiError(msg)
      setSubmitting(false)
      return
    }
  }

  function downloadReport() {
    if (!status?.report_url) return
    const url = status.report_url
    window.open(url, '_blank')
  }

  return (
    <div className="container" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
      <div className="header" style={{ textAlign: 'center', color: '#fff', margin: '40px 0' }}>
        <h1 style={{ fontSize: '3rem', fontWeight: 700 }}><i className="fas fa-chart-line" /> Trading Analyzer</h1>
        <p>Analyseur de Trading Professionnel - Interface Web</p>
      </div>

      <div className="main-card" style={{ background: '#fff', borderRadius: 20, boxShadow: '0 20px 60px rgba(0,0,0,0.15)', overflow: 'hidden' }}>
        <div className="card-header" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: '#fff', padding: 30, textAlign: 'center' }}>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 600 }}><i className="fas fa-upload" /> Analyse de Vos Fichiers de Trading</h2>
          <p>Déposez vos fichiers Excel pour obtenir une analyse complète et détaillée</p>
        </div>
        <div className="card-body" style={{ padding: 40 }}>
          <div
            className={`upload-zone${isDragOver ? ' dragover' : ''}`}
            onClick={() => (document.getElementById('fileInput') as HTMLInputElement)?.click()}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            style={{
              border: '3px dashed #667eea',
              borderRadius: 15,
              padding: '60px 20px',
              textAlign: 'center',
              background: isDragOver ? '#e8ebff' : '#f8f9ff',
              marginBottom: 30,
              cursor: 'pointer',
              transition: 'all .2s ease'
            }}
          >
            <div className="upload-icon" style={{ fontSize: '4rem', color: '#667eea', marginBottom: 20 }}>
              <i className="fas fa-cloud-upload-alt" />
            </div>
            <h3 style={{ fontSize: '1.5rem', color: '#333', fontWeight: 600, marginBottom: 10 }}>Glissez vos fichiers ici</h3>
            <p style={{ color: '#666', marginBottom: 20 }}>ou cliquez pour sélectionner vos fichiers Excel (.xlsx, .xls)</p>
            <button type="button" className="btn" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: '#fff', padding: '15px 30px', borderRadius: 10, border: 0 }}>
              <i className="fas fa-folder-open" /> Sélectionner les fichiers
            </button>
            <input id="fileInput" type="file" multiple accept=".xlsx,.xls" style={{ display: 'none' }} onChange={onFileChange} />
          </div>

          {files.length > 0 && (
            <div className="file-list" style={{ marginTop: 20 }}>
              {files.map((f, idx) => (
                <div key={f.name} className="file-item" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#fff', border: '1px solid #e8ebff', borderRadius: 10, padding: 15, marginBottom: 10 }}>
                  <div className="file-info" style={{ display: 'flex', alignItems: 'center', gap: 15 }}>
                    <div className="file-icon" style={{ fontSize: '1.5rem', color: '#667eea' }}>
                      <i className="fas fa-file-excel" />
                    </div>
                    <div className="file-details">
                      <h4 style={{ margin: 0, color: '#333' }}>{f.name}</h4>
                      <p style={{ margin: 0, color: '#666', fontSize: '.9rem' }}>{(f.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                  </div>
                  <button
                    aria-label={`Supprimer ${f.name}`}
                    onClick={() => setFiles(prev => prev.filter((_, i) => i !== idx))}
                    style={{ background: '#ff6b6b', color: '#fff', border: 0, borderRadius: '50%', width: 30, height: 30 }}
                  >
                    <i className="fas fa-times" />
                  </button>
                </div>
              ))}
            </div>
          )}
          {uiError && (
            <div className="error" style={{ marginTop: 10, color: '#b00020', fontWeight: 600 }}>{uiError}</div>
          )}

          <div className="options-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 30, marginBottom: 30 }}>
            <div className="option-group" style={{ background: '#f8f9ff', borderRadius: 15, padding: 25, border: '2px solid #e8ebff' }}>
              <label style={{ fontWeight: 600, color: '#333', marginBottom: 15, display: 'block' }}><i className="fas fa-filter" /> Type d'analyse</label>
              <div className="radio-group" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <label className="radio-option" style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <input type="radio" name="filter_type" value="tous" checked={filter === 'tous'} onChange={() => setFilter('tous')} /> Tous les instruments
                </label>
                <label className="radio-option" style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <input type="radio" name="filter_type" value="forex" checked={filter === 'forex'} onChange={() => setFilter('forex')} /> Forex uniquement
                </label>
                <label className="radio-option" style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <input type="radio" name="filter_type" value="autres" checked={filter === 'autres'} onChange={() => setFilter('autres')} /> Autres instruments
                </label>
              </div>
            </div>
            <div className="option-group" style={{ background: '#f8f9ff', borderRadius: 15, padding: 25, border: '2px solid #e8ebff' }}>
              <label htmlFor="soldeInitial" style={{ fontWeight: 600, color: '#333', marginBottom: 15, display: 'block' }}><i className="fas fa-euro-sign" /> Solde initial</label>
              <input id="soldeInitial" type="number" value={solde} onChange={e => setSolde(e.target.value)} min={100} step={100} placeholder="Entrez votre solde initial" className="number-input" style={{ width: '100%', padding: 15, border: '2px solid #e8ebff', borderRadius: 10 }} />
              <div style={{ height: 14 }} />
              <label htmlFor="multiplier" style={{ fontWeight: 600, color: '#333', marginBottom: 8, display: 'block' }}><i className="fas fa-times" /> Multiplicateur</label>
              <select id="multiplier" value={multiplier} onChange={e => setMultiplier(e.target.value)} style={{ width: '100%', padding: 12, border: '2px solid #e8ebff', borderRadius: 10 }}>
                <option value="1">x1 (défaut)</option>
                <option value="2">x2</option>
                <option value="3">x3</option>
                <option value="4">x4</option>
                <option value="5">x5</option>
              </select>
            </div>
          </div>

          <div style={{ textAlign: 'center' }}>
            <button onClick={startAnalyze} disabled={!canAnalyze || submitting} className="btn btn-success" style={{ background: 'linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%)', color: '#fff', padding: '15px 30px', borderRadius: 10, border: 0, minWidth: 220 }}>
              {submitting ? <span><span className="loading-spinner" style={{ display: 'inline-block', width: 16, height: 16, border: '3px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%', marginRight: 8, verticalAlign: 'middle', animation: 'spin 1s linear infinite' }} /> Analyse en cours…</span> : <span><i className="fas fa-play" /> Lancer l'analyse</span>}
            </button>
          </div>
        </div>
      </div>

      {status && (
        <div className="progress-container" style={{ background: '#fff', borderRadius: 15, padding: 30, marginTop: 30, boxShadow: '0 10px 30px rgba(0,0,0,0.1)' }}>
          <div className="progress-header" style={{ textAlign: 'center', marginBottom: 20 }}>
            <h3><i className="fas fa-cogs" /> Analyse en cours...</h3>
            <p className="progress-status">{status.message}</p>
          </div>
          <div className="progress-bar-container" style={{ background: '#f0f2ff', borderRadius: 25, height: 20, overflow: 'hidden', marginBottom: 12 }}>
            <div className="progress-bar" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', height: '100%', width: `${status.progress || 0}%`, transition: 'width 0.5s ease' }} />
          </div>
          <div className="progress-percentage" style={{ textAlign: 'center', fontWeight: 600 }}>{status.progress || 0}%</div>
        </div>
      )}

      {status?.statistics && (
        <div className="results-container" style={{ background: '#fff', borderRadius: 15, padding: 30, marginTop: 30, boxShadow: '0 10px 30px rgba(0,0,0,0.1)' }}>
          <div className="results-header" style={{ textAlign: 'center', marginBottom: 20 }}>
            <div className="success-icon" style={{ fontSize: '3rem', color: '#56ab2f' }}><i className="fas fa-check-circle" /></div>
            <h3>Analyse terminée avec succès !</h3>
          </div>

          {/* Filtres (paires + dates) */}
            <div className="option-group" style={{ background: '#f8f9ff', borderRadius: 15, padding: 20, border: '2px solid #e8ebff', marginBottom: 16 }}>
            <label style={{ fontWeight: 600, color: '#333', marginBottom: 10, display: 'block' }}><i className="fas fa-filter" /> Filtres d'affichage</label>
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: 14, alignItems: 'start' }}>
              <div>
                <div style={{ fontWeight: 600, color: '#333', marginBottom: 6 }}>Paires</div>
                <div className="chips-container" style={{ display: 'flex', flexWrap: 'wrap', gap: 8, border: '2px solid #e8ebff', borderRadius: 8, padding: 10, background: '#fff', minHeight: 44 }}>
                  {pairs.map(p => {
                    const isSel = selectedPairs.has(p)
                    return (
                      <div
                        key={p}
                        className={`chip${isSel ? ' selected' : ''}`}
                        onClick={() => {
                          // ne pas mettre à jour les graphiques instantanément; on attend "Appliquer les filtres"
                          setSelectedPairs(prev => {
                            const next = new Set(prev)
                            if (next.has(p)) next.delete(p); else next.add(p)
                            return next
                          })
                        }}
                        style={{ padding: '8px 12px', borderRadius: 999, border: `1px solid ${isSel ? '#667eea' : '#d6dcff'}`, cursor: 'pointer', background: isSel ? '#667eea' : '#f7f8ff', color: isSel ? '#fff' : '#333', fontWeight: 600 }}
                      >{p}</div>
                    )
                  })}
                </div>
                <div style={{ marginTop: 8, display: 'flex', gap: 8 }}>
                  <button className="btn" type="button" style={{ padding: '8px 12px', fontSize: '.9rem' }} onClick={() => { setSelectedPairs(new Set(pairs)) }}>Tout sélectionner</button>
                  <button className="btn" type="button" style={{ padding: '8px 12px', fontSize: '.9rem' }} onClick={() => { setSelectedPairs(new Set()) }}>Vider</button>
                </div>
              </div>
              <div>
                <div style={{ fontWeight: 600, color: '#333', marginBottom: 6 }}>Date début</div>
                <input type="date" className="number-input" value={dateStart} onChange={e => setDateStart(e.target.value)} style={{ width: '100%', padding: 12, border: '2px solid #e8ebff', borderRadius: 10 }} />
              </div>
              <div>
                <div style={{ fontWeight: 600, color: '#333', marginBottom: 6 }}>Date fin</div>
                <input type="date" className="number-input" value={dateEnd} onChange={e => setDateEnd(e.target.value)} style={{ width: '100%', padding: 12, border: '2px solid #e8ebff', borderRadius: 10 }} />
              </div>
            </div>
            <div style={{ marginTop: 10 }}>
              <button
                className="btn btn-outline"
                type="button"
                onClick={async () => {
                  if (!taskId) return
                  try {
                    const payload = {
                      pairs: Array.from(selectedPairs),
                      date_start: dateStart || null,
                      date_end: dateEnd || null
                    }
                    const { data } = await axios.post(`/filter_stats/${taskId}`, payload)
                    if (data?.success) {
                      // si aucune paire sélectionnée, on affiche un état vide cohérent
                      const stats = (Array.isArray(payload.pairs) && payload.pairs.length === 0) ? buildEmptyStatistics(status?.statistics) : data.statistics
                      setStatus(prev => prev ? { ...prev, statistics: stats } : prev)
                    }
                  } catch {}
                }}
              >
                <i className="fas fa-sliders-h" /> Appliquer les filtres
              </button>
            </div>
          </div>

          <div className="stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 20, marginBottom: 20 }}>
            {[{
              icon: 'fas fa-chart-line', value: status.statistics?.total_trades ?? 0, label: 'Total Trades', color: '#667eea'
            }, {
              icon: 'fas fa-euro-sign', value: `${status.statistics?.profit_compose ?? 0} €`, label: 'Profit Composé', color: (status.statistics?.profit_compose ?? 0) >= 0 ? '#56ab2f' : '#e53e3e'
            }, {
              icon: 'fas fa-percentage', value: `${status.statistics?.rendement_pct ?? 0}%`, label: 'Rendement', color: (status.statistics?.rendement_pct ?? 0) >= 0 ? '#56ab2f' : '#e53e3e'
            }, {
              icon: 'fas fa-bullseye', value: `${status.statistics?.taux_reussite ?? 0}%`, label: 'Taux Réussite', color: '#667eea'
            }, {
              icon: 'fas fa-piggy-bank', value: `${status.statistics?.solde_final ?? 0} €`, label: 'Solde Final', color: '#56ab2f'
            }, {
              icon: 'fas fa-chart-bar', value: `${status.statistics?.pips_totaux ?? 0}`, label: 'Pips/Points Totaux', color: (status.statistics?.pips_totaux ?? 0) >= 0 ? '#56ab2f' : '#e53e3e'
            }, {
              icon: 'fas fa-check', value: `${status.statistics?.trades_gagnants ?? 0}`, label: 'Trades Gagnants', color: '#56ab2f'
            }, {
              icon: 'fas fa-arrow-down', value: `${status.statistics?.drawdown_max ?? 0}%`, label: 'Drawdown Max', color: '#e53e3e'
            }].map((card, i) => (
              <div key={i} className="stat-card" style={{ background: '#f8f9ff', borderRadius: 12, padding: 20, textAlign: 'center', border: '2px solid #e8ebff' }}>
                <div className="stat-icon" style={{ fontSize: '2rem', marginBottom: 10, color: card.color }}><i className={card.icon} /></div>
                <div className="stat-value" style={{ fontSize: '1.5rem', fontWeight: 700, color: card.color }}>{card.value}</div>
                <div className="stat-label" style={{ color: '#666' }}>{card.label}</div>
              </div>
            ))}
          </div>

          {Array.isArray(status.statistics.evolution_somme_cumulee) && (status.statistics.evolution_somme_cumulee as any[]).length > 0 && (
            <Section title="Évolution de la somme cumulée" icon="fas fa-chart-line" defaultOpen>
              <div style={{ height: 360 }}>
                <SafeLine
                  data={{
                    labels: (Array.isArray(status.statistics.evolution_somme_cumulee) ? status.statistics.evolution_somme_cumulee : []).map((p: any) => new Date(p?.date ?? '').toLocaleString('fr-FR')),
                    datasets: [{
                      label: 'Solde cumulé (€)',
                      data: (Array.isArray(status.statistics.evolution_somme_cumulee) ? status.statistics.evolution_somme_cumulee : []).map((p: any) => p?.solde ?? 0),
                      borderColor: 'rgba(102,126,234,1)',
                      backgroundColor: 'rgba(102,126,234,0.15)',
                      borderWidth: 2,
                    }]
                  }}
                  options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true, position: 'top' } } }}
                />
              </div>
            </Section>
          )}

          {/* Performance par session (Total) */}
          {!!status.statistics.sessions_total && (
            <Section title="Performance par session (Total)" icon="fas fa-globe">
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
                <div style={{ height: 280 }}>
                  <SafeBar
                    data={() => ((() => {
                      const labels = ['Asie','Europe','Amérique']
                      const src = status.statistics.sessions_total?.taux_reussite_in_pct || {}
                      return { labels, datasets: [{ label: 'Taux de réussite IN (%)', data: labels.map(l => src[l] || 0), backgroundColor: ['#6687ea','#56ab2f','#e53e3e'].map(c=>c+'AA') }] }
                    })())}
                    options={{ responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, max: 100 } } }}
                  />
                </div>
                <div style={{ height: 280 }}>
                  <SafeBar
                    data={() => ((() => {
                      const labels = ['Asie','Europe','Amérique']
                      const src = status.statistics.sessions_total?.pnl_out || {}
                      return { labels, datasets: [{ label: 'PnL (€) au dernier OUT', data: labels.map(l => src[l] || 0), backgroundColor: 'rgba(118,75,162,0.6)' }] }
                    })())}
                    options={{ responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }}
                  />
                </div>
              </div>
              <div style={{ marginTop: 20, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
                <div style={{ height: 260 }}>
                  <SafeBar
                    data={() => ((() => {
                      const labels = ['Asie','Europe','Amérique']
                      const src = status.statistics.sessions_total?.tp_out || {}
                      return { labels, datasets: [{ label: 'TP (nb)', data: labels.map(l => src[l] || 0), backgroundColor: 'rgba(86,171,47,0.7)' }] }
                    })())}
                    options={{ responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }}
                  />
                </div>
                <div style={{ height: 260 }}>
                  <SafeBar
                    data={() => ((() => {
                      const labels = ['Asie','Europe','Amérique']
                      const src = status.statistics.sessions_total?.sl_out || {}
                      return { labels, datasets: [{ label: 'SL (nb)', data: labels.map(l => src[l] || 0), backgroundColor: 'rgba(229,62,62,0.7)' }] }
                    })())}
                    options={{ responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }}
                  />
                </div>
              </div>
            </Section>
          )}

          {/* Répartition IN/OUT par heure */}
          <Section title="Répartition des IN/OUT" icon="fas fa-sign-in-alt">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
              {!!chartInData && <div style={{ height: 260 }}><SafeBar data={chartInData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true } } }} /></div>}
              {!!chartOutData && <div style={{ height: 260 }}><SafeBar data={chartOutData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true } } }} /></div>}
            </div>
          </Section>

          {/* Profits vs pertes: heure, jour, mois */}
          <Section title="Profits vs Pertes" icon="fas fa-euro-sign">
            <div style={{ marginBottom: 16, height: 260 }}>
              {!!chartPLHourData && <SafeBar data={chartPLHourData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true } } }} />}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
              {!!chartPLDayData && <div style={{ height: 240 }}><SafeBar data={chartPLDayData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true } } }} /></div>}
              {!!chartPLMonthData && <div style={{ height: 240 }}><SafeBar data={chartPLMonthData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true } } }} /></div>}
            </div>
          </Section>

          {/* TP vs SL: heure, jour, mois */}
          <Section title="TP vs SL" icon="fas fa-bullseye">
            <div style={{ marginBottom: 16, height: 260 }}>
              {!!chartTPHourData && <SafeBar data={chartTPHourData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true } } }} />}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
              {!!chartTPDayData && <div style={{ height: 240 }}><SafeBar data={chartTPDayData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true } } }} /></div>}
              {!!chartTPMonthData && <div style={{ height: 240 }}><SafeBar data={chartTPMonthData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true } } }} /></div>}
            </div>
          </Section>

          {/* Temps moyen des trades */}
          {(status.statistics.duree_moyenne_minutes != null || status.statistics.duree_mediane_minutes != null) && (
            <Section title="Temps moyen des trades" icon="fas fa-hourglass-half">
              <div style={{ fontWeight: 600, color: '#333' }}>
                {(() => {
                  const avg = status.statistics.duree_moyenne_minutes
                  const med = status.statistics.duree_mediane_minutes
                  const toText = (m: number) => {
                    const h = Math.floor(m / 60); const mn = Math.round(m % 60)
                    return h > 0 ? `${h}h ${mn}m` : `${mn} minutes`
                  }
                  const avgTxt = avg != null ? `Moyenne: ${toText(avg)}` : ''
                  const medTxt = med != null ? ` | Médiane: ${toText(med)}` : ''
                  return avgTxt + medTxt
                })()}
              </div>
            </Section>
          )}

          {status.report_url && (
            <div className="download-section" style={{ textAlign: 'center', paddingTop: 20 }}>
              <button onClick={downloadReport} className="btn btn-outline"><i className="fas fa-file-excel" /> Télécharger le rapport Excel</button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}


