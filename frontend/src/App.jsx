import { useState } from 'react'
import axios from 'axios'

export default function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [includeReport, setIncludeReport] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!url.trim()) return

    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(
        '/api/summarize-html',
        {
          url: url,
          include_detailed_report: includeReport,
        },
        { responseType: 'blob' }
      )

      // HTMLをブラウザで開く
      const blob = new Blob([response.data], { type: 'text/html' })
      const htmlUrl = window.URL.createObjectURL(blob)
      window.open(htmlUrl, '_blank')

      // フォームをリセット
      setUrl('')
      setIncludeReport(false)
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        'エラーが発生しました'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-lg shadow-2xl p-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2 text-center">
            YouTube Summarizer
          </h1>
          <p className="text-gray-600 text-center mb-8 text-sm">
            YouTubeビデオをAIでサマライズ。HTMLレポート生成
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="url" className="block text-sm font-semibold text-gray-700 mb-2">
                ビデオURL
              </label>
              <input
                type="url"
                id="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                required
                disabled={loading}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500 transition disabled:bg-gray-100"
              />
            </div>

            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={includeReport}
                onChange={(e) => setIncludeReport(e.target.checked)}
                disabled={loading}
                className="w-4 h-4 text-indigo-600 rounded"
              />
              <span className="ml-3 text-sm text-gray-700">
                詳細レポートも生成する
              </span>
            </label>

            <button
              type="submit"
              disabled={loading || !url.trim()}
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <span className="inline-block animate-spin mr-2">⏳</span>
                  処理中...
                </span>
              ) : (
                'レポートを生成'
              )}
            </button>
          </form>

          {error && (
            <div className="mt-6 bg-red-50 border-2 border-red-200 rounded-lg p-4">
              <p className="text-red-700 text-sm">
                <span className="font-semibold">エラー:</span> {error}
              </p>
            </div>
          )}

          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">
              ✓ 音声をテキスト化<br />
              ✓ AIでサマライズ<br />
              ✓ 重要シーン抽出<br />
              ✓ HTMLレポート生成
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
