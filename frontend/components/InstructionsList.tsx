"use client";

import { useState } from "react";

interface Field {
  field_name: string;
  field_type: string;
  suggested_value?: string | null;
  instructions: string;
  warning?: string | null;
}

interface InstructionsListProps {
  fields: Field[];
}

export default function InstructionsList({ fields }: InstructionsListProps) {
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());

  const toggleStep = (index: number) => {
    setCompletedSteps((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  const progress = Math.round((completedSteps.size / fields.length) * 100);

  return (
    <div className="space-y-4">
      {/* Progress bar */}
      <div className="flex items-center gap-3">
        <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-500 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <span className="text-xs text-slate-500 font-medium w-12 text-right">
          {completedSteps.size}/{fields.length}
        </span>
      </div>

      {/* Steps */}
      <ol className="space-y-3">
        {fields.map((field, index) => {
          const done = completedSteps.has(index);
          return (
            <li
              key={index}
              onClick={() => toggleStep(index)}
              className={`flex gap-3 rounded-lg border p-4 cursor-pointer select-none transition-all duration-150 ${
                done
                  ? "border-green-200 bg-green-50"
                  : "border-slate-200 bg-white hover:border-blue-200 hover:bg-blue-50/30"
              }`}
            >
              {/* Step circle */}
              <div
                className={`flex-shrink-0 w-7 h-7 rounded-full border-2 flex items-center justify-center transition-colors ${
                  done
                    ? "border-green-500 bg-green-500 text-white"
                    : "border-slate-300 bg-white text-slate-500"
                }`}
              >
                {done ? (
                  <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                ) : (
                  <span className="text-xs font-bold">{index + 1}</span>
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <p
                    className={`text-sm font-semibold ${
                      done ? "text-green-700 line-through" : "text-slate-800"
                    }`}
                  >
                    {field.field_name}
                  </p>
                  {field.suggested_value && (
                    <code className="text-xs bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded font-mono truncate max-w-[160px]">
                      {field.suggested_value}
                    </code>
                  )}
                </div>
                <p className={`text-sm ${done ? "text-green-600" : "text-slate-600"}`}>
                  {field.instructions}
                </p>
                {field.warning && !done && (
                  <p className="mt-1 text-xs text-amber-700 flex items-center gap-1">
                    <span>&#9888;</span> {field.warning}
                  </p>
                )}
              </div>
            </li>
          );
        })}
      </ol>

      {completedSteps.size === fields.length && fields.length > 0 && (
        <div className="rounded-lg bg-green-50 border border-green-200 p-4 text-center">
          <p className="text-green-700 font-semibold text-sm">All fields completed!</p>
          <p className="text-green-600 text-xs mt-1">Review your entries before submitting the form.</p>
        </div>
      )}
    </div>
  );
}
