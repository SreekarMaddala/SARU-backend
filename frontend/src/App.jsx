import React, { useEffect, useState } from 'react'
import FeedbackTable from './components/FeedbackTable'

function App() {
  const [feedbacks, setFeedbacks] = useState([])

  useEffect(() => {
    fetch('http://localhost:8000/feedback')
      .then((res) => res.json())
      .then((data) => setFeedbacks(data))
      .catch((err) => console.error('Error fetching feedback:', err))
  }, [])

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-3xl font-bold mb-6">Feedback Collector MVP 🚀</h1>
      <FeedbackTable feedbacks={feedbacks} />
    </div>
  )
}

export default App
