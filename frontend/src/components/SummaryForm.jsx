import { useState } from 'react'

export default function SummaryForm({ onSubmit, disabled }) {
  const [url, setUrl] = useState('')
  const [detailedReport, setDetailedReport] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (url.trim()) {
      onSubmit(url, detailedReport)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
          YouTubeビデオのURL
        </label>
        <input
          type="url"
          id="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://www.youtube.com/watch?v=..."
          required
          disabled={disabled}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition disabled:bg-gray-100"
        />
        <p className="text-sm text-gray-500 mt-2">
          YouTube、YouTubeShorts、その他のYouTubeプラットフォームのURLをサポートしています
        </p>
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="detailed"
          checked={detailedReport}
          onChange={(e) => setDetailedReport(e.target.checked)}
          disabled={disabled}
          className="w-4 h-4 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
        />
        <label htmlFor="detailed" className="ml-2 text-sm text-gray-700">
          詳細レポートも生成する（処理時間が長くなります）
        </label>
      </div>

      <button
        type="submit"
        disabled={disabled || !url.trim()}
        className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {disabled ? 'サマライズ中...' : 'サマライズを開始'}
      </button>
    </form>
  )
}
