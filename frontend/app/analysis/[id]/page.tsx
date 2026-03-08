"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import FieldAnnotation from "@/components/FieldAnnotation";
import InstructionsList from "@/components/InstructionsList";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8003";

interface Field {
  field_name: string;
  field_type: string;
  suggested_value?: string | null;
  instructions: string;
  warning?: string | null;
  position?: { x: number; y: number } | null;
}

interface Analysis {
  id: number;
  image_path: string;
  user_context: string;
  fields: Field[];
  summary?: string | null;
  created_at: string;
  is_mock: boolean;
}

type ViewMode = "annotations" | "steps";

export default function AnalysisPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;

  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<ViewMode>("annotations");

  useEffect(() => {
    if (!id) return;
    fetch(`${API_BASE}/api/analyses/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to load analysis (${res.status})`);
        return res.json();
      })
      .then((data) => {
        setAnalysis(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-3 text-slate-500">
          <svg className="w-8 h-8 animate-spin text-blue-500" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <span className="text-sm">Loading analysis...</span>
        </div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <p className="text-red-600 font-medium mb-3">{error ?? "Analysis not found"}</p>
          <button
            onClick={() => router.push("/")}
            className="text-sm text-blue-600 hover:underline"
          >
            Go back home
          </button>
        </div>
      </div>
    );
  }

  const imageUrl = `${API_BASE}${analysis.image_path}`;

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.push("/")}
              className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-600 transition-colors"
              aria-label="Back"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-md bg-blue-600 flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <span className="font-bold text-slate-900">FormPilot</span>
            </div>
          </div>
          <a href="/history" className="text-sm text-slate-600 hover:text-blue-600 font-medium">
            History
          </a>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Summary bar */}
        <div className="flex flex-wrap items-center gap-3 mb-6">
          <div className="flex-1">
            <h1 className="text-xl font-bold text-slate-900">Form Analysis</h1>
            {analysis.summary && (
              <p className="text-sm text-slate-500 mt-0.5">{analysis.summary}</p>
            )}
          </div>
          {analysis.is_mock && (
            <span className="text-xs font-medium bg-amber-100 text-amber-700 border border-amber-200 rounded-full px-3 py-1">
              Sample data (no API key)
            </span>
          )}
          <span className="text-xs text-slate-500">
            {analysis.fields.length} field{analysis.fields.length !== 1 ? "s" : ""} detected
          </span>
        </div>

        {/* View mode toggle */}
        <div className="flex rounded-lg border border-slate-200 bg-white p-1 w-fit mb-6 shadow-sm">
          {(["annotations", "steps"] as ViewMode[]).map((mode) => (
            <button
              key={mode}
              onClick={() => setView(mode)}
              className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors capitalize ${
                view === mode
                  ? "bg-blue-600 text-white"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              {mode === "annotations" ? "Field Cards" : "Step-by-Step"}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left: form image with position overlays */}
          <div className="space-y-4">
            <h2 className="text-sm font-semibold text-slate-600 uppercase tracking-wide">
              Form Preview
            </h2>
            <div className="relative rounded-xl overflow-hidden border border-slate-200 bg-white shadow-sm">
              <img
                src={imageUrl}
                alt="Uploaded form"
                className="w-full object-contain"
              />
              {/* Position overlays for fields that have coordinates */}
              {analysis.fields.map((field, i) =>
                field.position ? (
                  <div
                    key={i}
                    className="absolute"
                    style={{
                      left: `${field.position.x}%`,
                      top: `${field.position.y}%`,
                      transform: "translate(-50%, -50%)",
                    }}
                  >
                    <div className="w-6 h-6 rounded-full bg-blue-600 border-2 border-white shadow-lg flex items-center justify-center text-white text-xs font-bold">
                      {i + 1}
                    </div>
                  </div>
                ) : null
              )}
            </div>

            {/* Context */}
            {analysis.user_context && (
              <div className="rounded-lg border border-slate-200 bg-white p-4">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                  Your context
                </p>
                <p className="text-sm text-slate-700">{analysis.user_context}</p>
              </div>
            )}
          </div>

          {/* Right: field analysis */}
          <div className="space-y-4">
            <h2 className="text-sm font-semibold text-slate-600 uppercase tracking-wide">
              {view === "annotations" ? "Field Analysis" : "Instructions"}
            </h2>

            {view === "annotations" ? (
              <div className="space-y-3">
                {analysis.fields.map((field, i) => (
                  <FieldAnnotation key={i} field={field} index={i} />
                ))}
              </div>
            ) : (
              <InstructionsList fields={analysis.fields} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
