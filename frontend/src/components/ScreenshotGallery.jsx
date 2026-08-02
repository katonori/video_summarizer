import { useState } from 'react'

export default function ScreenshotGallery({ screenshots }) {
  const [selectedIndex, setSelectedIndex] = useState(0)

  return (
    <div className="space-y-4">
      {/* メイン画像 */}
      <div className="relative bg-gray-900 rounded-lg overflow-hidden">
        <img
          src={screenshots[selectedIndex]}
          alt={`Screenshot ${selectedIndex + 1}`}
          className="w-full h-auto max-h-96 object-cover"
        />
      </div>

      {/* サムネイル */}
      <div className="overflow-x-auto">
        <div className="flex gap-2">
          {screenshots.map((screenshot, index) => (
            <button
              key={index}
              onClick={() => setSelectedIndex(index)}
              className={`flex-shrink-0 rounded-lg overflow-hidden border-2 transition ${
                index === selectedIndex
                  ? 'border-indigo-600'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <img
                src={screenshot}
                alt={`Thumbnail ${index + 1}`}
                className="w-20 h-20 object-cover"
              />
            </button>
          ))}
        </div>
      </div>

      {/* ナビゲーション */}
      <div className="flex items-center justify-between text-sm text-gray-600">
        <span>
          {selectedIndex + 1} / {screenshots.length}
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => setSelectedIndex(Math.max(0, selectedIndex - 1))}
            disabled={selectedIndex === 0}
            className="px-3 py-1 bg-gray-200 rounded disabled:bg-gray-100 disabled:text-gray-400"
          >
            ←
          </button>
          <button
            onClick={() => setSelectedIndex(Math.min(screenshots.length - 1, selectedIndex + 1))}
            disabled={selectedIndex === screenshots.length - 1}
            className="px-3 py-1 bg-gray-200 rounded disabled:bg-gray-100 disabled:text-gray-400"
          >
            →
          </button>
        </div>
      </div>
    </div>
  )
}
