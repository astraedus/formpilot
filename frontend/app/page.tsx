"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import DropZone from "@/components/DropZone";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8003";

export default function HomePage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [context, setContext] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = useCallback((f: File) => {
    setFile(f);
    setError(null);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please upload a form screenshot first.");
      return;
    }
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("user_context", context);

      const res = await fetch(`${API_BASE}/api/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail ?? `Server error: ${res.status}`);
      }

      const analysis = await res.json();
      router.push(`/analysis/${analysis.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred.");
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <span className="text-lg font-bold text-slate-900">FormPilot</span>
          </div>
          <a
            href="/history"
            className="text-sm text-slate-600 hover:text-blue-600 transition-colors font-medium"
          >
            History
          </a>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-4xl mx-auto px-4 pt-12 pb-8 text-center">
        <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight mb-3">
          Navigate any form,{" "}
          <span className="text-blue-600">instantly</span>
        </h1>
        <p className="text-lg text-slate-600 max-w-xl mx-auto">
          Upload a screenshot of any form. FormPilot uses Gemini Vision to analyze every field and
          give you step-by-step fill instructions and auto-fill suggestions.
        </p>
      </section>

      {/* Upload card */}
      <section className="max-w-2xl mx-auto px-4 pb-16">
        <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-md border border-slate-200 p-8 space-y-6">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              Form screenshot
              <span className="text-red-500 ml-1">*</span>
            </label>
            <DropZone onFileSelect={handleFileSelect} />
          </div>

          <div>
            <label htmlFor="context" className="block text-sm font-semibold text-slate-700 mb-1">
              Your context
              <span className="text-slate-400 font-normal ml-2">(optional but recommended)</span>
            </label>
            <textarea
              id="context"
              value={context}
              onChange={(e) => setContext(e.target.value)}
              rows={4}
              placeholder="e.g. I'm a 32-year-old software engineer in San Francisco applying for a California driver's license renewal. My address is 123 Main St, SF, CA 94102."
              className="w-full rounded-lg border border-slate-300 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition"
            />
            <p className="text-xs text-slate-500 mt-1">
              The more context you give, the better the fill suggestions.
            </p>
          </div>

          {error && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !file}
            className="w-full bg-blue-600 text-white font-semibold rounded-lg py-3 px-6 hover:bg-blue-700 active:bg-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-150 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Analyzing form...
              </>
            ) : (
              "Analyze Form"
            )}
          </button>
        </form>

        {/* Features row */}
        <div className="mt-8 grid grid-cols-3 gap-4 text-center">
          {[
            { icon: "M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z", label: "Vision-powered", sub: "Gemini 2.0 Flash" },
            { icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4", label: "Step-by-step", sub: "Field instructions" },
            { icon: "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z", label: "History", sub: "Past analyses saved" },
          ].map((f) => (
            <div key={f.label} className="bg-white rounded-xl border border-slate-200 p-4">
              <div className="w-9 h-9 rounded-lg bg-blue-100 flex items-center justify-center mx-auto mb-2">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={f.icon} />
                </svg>
              </div>
              <p className="text-sm font-semibold text-slate-800">{f.label}</p>
              <p className="text-xs text-slate-500">{f.sub}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
