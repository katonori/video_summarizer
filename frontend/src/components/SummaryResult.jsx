import ScreenshotGallery from './ScreenshotGallery'

export default function SummaryResult({ result }) {
  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)

    if (hours > 0) {
      return `${hours}時間 ${minutes}分 ${secs}秒`
    }
    return `${minutes}分 ${secs}秒`
  }

  return (
    <div className="space-y-8">
      {/* ビデオ情報 */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">{result.title}</h2>
        <div className="grid grid-cols-3 gap-4 text-sm text-gray-600 mb-4">
          <div>
            <span className="font-semibold">長さ：</span>
            {formatDuration(result.duration)}
          </div>
          <div>
            <span className="font-semibold">Video ID：</span>
            {result.video_id}
          </div>
        </div>
        {result.description && (
          <p className="text-gray-700 text-sm leading-relaxed">
            {result.description}
          </p>
        )}
      </div>

      {/* スクリーンショット */}
      {result.screenshots.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">ビデオスクリーンショット</h3>
          <ScreenshotGallery screenshots={result.screenshots} />
        </div>
      )}

      {/* サマリー */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">サマリー</h3>
        <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-line leading-relaxed">
          {result.summary}
        </div>
      </div>

      {/* 詳細レポート */}
      {result.detailed_report && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">詳細レポート</h3>
          <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-line leading-relaxed">
            {result.detailed_report}
          </div>
        </div>
      )}
    </div>
  )
}
