export default function LoadingSpinner() {
  return (
    <div className="mt-8 flex flex-col items-center justify-center py-12">
      <div className="relative w-16 h-16 mb-4">
        <div className="absolute inset-0 bg-gradient-to-r from-indigo-400 to-blue-400 rounded-full animate-spin"></div>
        <div className="absolute inset-2 bg-white rounded-full"></div>
      </div>
      <p className="text-gray-600 font-medium">ビデオをサマライズ中...</p>
      <p className="text-gray-500 text-sm mt-2">
        これには数分かかる場合があります
      </p>
      <div className="mt-4 space-y-2 text-sm text-gray-500">
        <p>✓ ビデオをダウンロード中</p>
        <p>✓ トランスクリプトを生成中</p>
        <p>⏳ サマリーを生成中...</p>
      </div>
    </div>
  )
}
