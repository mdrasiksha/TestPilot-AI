import React from "react";

const dummyTestCases = [
  {
    id: "TC-001",
    steps: "Open the app and enter a valid requirement.",
    expectedResult: "Requirement text is visible in the textarea.",
    priority: "High",
  },
  {
    id: "TC-002",
    steps: "Click the Generate Test Cases button.",
    expectedResult: "Test cases are shown in the output table.",
    priority: "Medium",
  },
  {
    id: "TC-003",
    steps: "Verify each row has ID, steps, expected result, and priority.",
    expectedResult: "All required columns are present and readable.",
    priority: "Low",
  },
];

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center px-4 py-8">
      <div className="w-full max-w-4xl space-y-6">
        <header className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">TestGen AI</h1>
        </header>

        <main className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <textarea
            placeholder="Paste your requirement here..."
            className="w-full h-36 border border-gray-300 rounded-md p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          <button
            type="button"
            className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700"
          >
            Generate Test Cases
          </button>
        </main>

        <section className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Output</h2>

          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="bg-gray-100 text-left">
                  <th className="border border-gray-200 p-2">Test Case ID</th>
                  <th className="border border-gray-200 p-2">Steps</th>
                  <th className="border border-gray-200 p-2">Expected Result</th>
                  <th className="border border-gray-200 p-2">Priority</th>
                </tr>
              </thead>
              <tbody>
                {dummyTestCases.map((testCase) => (
                  <tr key={testCase.id}>
                    <td className="border border-gray-200 p-2">{testCase.id}</td>
                    <td className="border border-gray-200 p-2">{testCase.steps}</td>
                    <td className="border border-gray-200 p-2">{testCase.expectedResult}</td>
                    <td className="border border-gray-200 p-2">{testCase.priority}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <footer className="text-center text-sm text-gray-500 pt-2">© 2026 TestPilot AI</footer>
      </div>
    </div>
  );
}
