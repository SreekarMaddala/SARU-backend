import React from 'react'

export default function FeedbackTable({ feedbacks }) {
  return (
    <table className="min-w-full bg-white border border-gray-300 rounded-md shadow-md">
      <thead>
        <tr className="bg-gray-200 text-gray-700">
          <th className="py-2 px-4 border-b border-gray-300">ID</th>
          <th className="py-2 px-4 border-b border-gray-300">Company ID</th>
          <th className="py-2 px-4 border-b border-gray-300">Channel</th>
          <th className="py-2 px-4 border-b border-gray-300">Text</th>
          <th className="py-2 px-4 border-b border-gray-300">Sentiment</th>
          <th className="py-2 px-4 border-b border-gray-300">Topics</th>
          <th className="py-2 px-4 border-b border-gray-300">Created At</th>
        </tr>
      </thead>
      <tbody>
        {feedbacks.map((fb) => (
          <tr key={fb.id} className="text-center border-b border-gray-300">
            <td className="py-2 px-4">{fb.id}</td>
            <td className="py-2 px-4">{fb.company_id}</td>
            <td className="py-2 px-4">{fb.channel}</td>
            <td className="py-2 px-4">{fb.text}</td>
            <td className="py-2 px-4">{fb.sentiment}</td>
            <td className="py-2 px-4">{fb.topics}</td>
            <td className="py-2 px-4">{new Date(fb.created_at).toLocaleString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
