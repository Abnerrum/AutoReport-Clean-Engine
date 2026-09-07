import { useState } from 'react'
import UploadZone from './components/UploadZone'
import ResultsView from './components/ResultsView'

export default function App() {
  const [status, setStatus] = useState('idle')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [fileName, setFileName] = useState('')

  const handleUpload = async (file) => {
    setFileName(file.name)
    setStatus('processing')
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch('/api/process', {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Erro ao processar arquivo')
      }
      setResult(data)
      setStatus('done')
    } catch (err) {
      setError(err.message)
      setStatus('error')
    }
  }

  const handleReset = () => {
    setStatus('idle')
    setResult(null)
    setError(null)
    setFileName('')
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="logo">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <line x1="3" y1="9" x2="21" y2="9" />
            <line x1="3" y1="15" x2="21" y2="15" />
            <line x1="9" y1="3" x2="9" y2="21" />
            <line x1="15" y1="3" x2="15" y2="21" />
          </svg>
          <h1>DataWrangler</h1>
        </div>
        <p className="tagline">Transforme arquivos brutos em relatórios estruturados</p>
      </header>

      <main className="app-main">
        {status === 'idle' && <UploadZone onUpload={handleUpload} />}

        {status === 'processing' && (
          <div className="processing">
            <div className="spinner" />
            <p className="processing-title">Processando <strong>{fileName}</strong>…</p>
            <p className="processing-hint">Aplicando algoritmos de limpeza e estruturação de dados</p>
          </div>
        )}

        {status === 'done' && (
          <ResultsView result={result} fileName={fileName} onReset={handleReset} />
        )}

        {status === 'error' && (
          <div className="error-view">
            <div className="error-icon">⚠</div>
            <p className="error-message">{error}</p>
            <button className="btn btn-primary" onClick={handleReset}>Tentar novamente</button>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Suporta CSV, Excel (.xlsx, .xls) e PDF com tabelas</p>
      </footer>
    </div>
  )
}
