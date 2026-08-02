import { useState } from 'react'
import axios from 'axios'
import SummaryForm from './components/SummaryForm'
import SummaryResult from './components/SummaryResult'
import LoadingSpinner from './components/LoadingSpinner'

export default function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (url, includeDetailedReport) => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await axios.post('/api/summarize', {
        url,
        include_detailed_report: includeDetailedReport,
      })
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error processing video. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-800 mb-2">
            YouTube Video Summarizer
          </h1>
          <p className="text-gray-600 text-lg">
            YouTubeビデオを瞬時にサマライズ。AI字幕を使用した要約とスクリーンショット
          </p>
        </header>

        <main className="max-w-4xl mx-auto">
          {!result ? (
            <div className="bg-white rounded-lg shadow-lg p-8">
              <SummaryForm onSubmit={handleSubmit} disabled={loading} />

              {loading && <LoadingSpinner />}

              {error && (
                <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              <SummaryResult result={result} />
              <button
                onClick={() => setResult(null)}
                className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition font-semibold"
              >
                別の動画をサマライズ
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
