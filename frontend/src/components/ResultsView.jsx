export default function ResultsView({ result, fileName, onReset }) {
  const { preview, summary, report_id } = result

  const handleDownload = () => {
    window.open(`/api/download/${report_id}`, '_blank')
  }

  return (
    <div className="results">
      <div className="results-header">
        <div>
          <h2>Relatório gerado</h2>
          <p className="filename">{fileName}</p>
        </div>
        <div className="results-actions">
          <button className="btn btn-primary" onClick={handleDownload}>
            ⬇ Baixar Excel
          </button>
          <button className="btn btn-secondary" onClick={onReset}>
            Novo arquivo
          </button>
        </div>
      </div>

      <div className="summary-cards">
        <div className="card">
          <span className="card-label">Linhas (antes)</span>
          <span className="card-value">{summary.original_rows}</span>
        </div>
        <div className="card">
          <span className="card-label">Linhas (depois)</span>
          <span className="card-value">{summary.cleaned_rows}</span>
        </div>
        <div className="card">
          <span className="card-label">Colunas</span>
          <span className="card-value">{summary.cleaned_cols}</span>
        </div>
        <div className="card">
          <span className="card-label">Duplicatas</span>
          <span className="card-value">{summary.duplicates}</span>
        </div>
      </div>

      <div className="section">
        <h3>Prévia dos dados limpos</h3>
        <p className="section-info">
          Mostrando {preview.rows.length} de {preview.total_rows} linhas
        </p>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                {preview.columns.map((col, i) => (
                  <th key={i}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {preview.rows.map((row, i) => (
                <tr key={i}>
                  {row.map((cell, j) => (
                    <td key={j}>{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="section">
        <h3>Informações das colunas</h3>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Coluna</th>
                <th>Tipo</th>
                <th>Não nulos</th>
                <th>Nulos</th>
                <th>Únicos</th>
              </tr>
            </thead>
            <tbody>
              {summary.columns.map((col, i) => (
                <tr key={i}>
                  <td>{col.name}</td>
                  <td><span className="type-badge">{col.dtype}</span></td>
                  <td>{col.non_null}</td>
                  <td>{col.null}</td>
                  <td>{col.unique}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
