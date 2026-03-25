'use client';

import { FormEvent, useMemo, useState } from 'react';

import { downloadUrl, fill, parse, sampleUpload, token, upload } from '../lib/api';
import { Placeholder } from '../lib/types';

type Step = 1 | 2 | 3 | 4;

function humanize(key: string) {
  return key
    .replace(/[._-]/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/\b\w/g, (m) => m.toUpperCase());
}

export default function HomePage() {
  const [step, setStep] = useState<Step>(1);
  const [jobId, setJobId] = useState<string>('');
  const [placeholders, setPlaceholders] = useState<Placeholder[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [error, setError] = useState<string>('');

  const grouped = useMemo(() => {
    return placeholders.reduce<Record<number, Placeholder[]>>((acc, p) => {
      acc[p.slideIndex] = acc[p.slideIndex] ?? [];
      acc[p.slideIndex].push(p);
      return acc;
    }, {});
  }, [placeholders]);

  const runParse = async (id: string) => {
    const parsed = await parse(id);
    setPlaceholders(parsed.placeholders);
    const defaults: Record<string, string> = {};
    parsed.placeholders.forEach((p) => {
      defaults[p.key] = '';
    });
    setAnswers(defaults);
    setStep(2);
  };

  async function onUpload(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError('');
    const input = (e.currentTarget.elements.namedItem('file') as HTMLInputElement) || null;
    const file = input?.files?.[0];
    if (!file) return;
    try {
      const { jobId: id } = await upload(file);
      setJobId(id);
      await runParse(id);
    } catch (err) {
      setError(String(err));
    }
  }

  async function onSample() {
    setError('');
    try {
      const { jobId: id } = await sampleUpload();
      setJobId(id);
      await runParse(id);
    } catch (err) {
      setError(String(err));
    }
  }

  async function onGenerate() {
    try {
      await fill(jobId, answers);
      setStep(4);
    } catch (err) {
      setError(String(err));
    }
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold">PPTX Autofill</h1>
        <p className="text-sm text-slate-600">Upload, detect placeholders, answer questions, and download generated PPTX.</p>
      </header>
      <p className="rounded bg-white p-3 text-xs shadow">API token via <code>NEXT_PUBLIC_APP_TOKEN</code> header <code>X-API-Token</code>. Current token: {token}</p>

      <ol className="grid grid-cols-4 gap-2 text-center text-sm">
        {[1, 2, 3, 4].map((s) => (
          <li key={s} className={`rounded p-2 ${step >= s ? 'bg-blue-600 text-white' : 'bg-slate-200'}`}>Step {s}</li>
        ))}
      </ol>

      {step === 1 && (
        <section className="rounded bg-white p-6 shadow space-y-4">
          <form onSubmit={onUpload} className="space-y-2">
            <input type="file" name="file" accept=".pptx" className="block" />
            <button className="rounded bg-blue-600 px-4 py-2 text-white">Upload Template</button>
          </form>
          <button className="rounded border px-4 py-2" onClick={onSample}>Use Sample Template</button>
        </section>
      )}

      {step === 2 && (
        <section className="rounded bg-white p-6 shadow">
          <h2 className="mb-3 text-xl font-semibold">Detected Fields & Mapping Preview</h2>
          <div className="space-y-3">
            {Object.entries(grouped).map(([slide, fields]) => (
              <div key={slide} className="rounded border p-3">
                <h3 className="font-medium">Slide {slide}</h3>
                <ul className="list-disc pl-5 text-sm">
                  {fields.map((field) => (
                    <li key={`${field.key}-${field.format}`}>{humanize(field.key)} ({field.suggestedType}) → {field.shapeName ?? 'shape'} | {field.context}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <button className="mt-4 rounded bg-blue-600 px-4 py-2 text-white" onClick={() => setStep(3)}>Continue to Form</button>
        </section>
      )}

      {step === 3 && (
        <section className="rounded bg-white p-6 shadow space-y-3">
          <h2 className="text-xl font-semibold">Fill Questionnaire</h2>
          {placeholders.map((p) => (
            <label key={p.key} className="block">
              <span className="mb-1 block text-sm font-medium">{humanize(p.key)} <small className="text-slate-500">({p.suggestedType})</small></span>
              {p.suggestedType === 'longtext' ? (
                <textarea className="w-full rounded border p-2" value={answers[p.key] ?? ''} onChange={(e) => setAnswers({ ...answers, [p.key]: e.target.value })} />
              ) : (
                <input
                  type={p.suggestedType === 'date' ? 'date' : p.suggestedType === 'number' ? 'number' : 'text'}
                  className="w-full rounded border p-2"
                  value={answers[p.key] ?? ''}
                  onChange={(e) => setAnswers({ ...answers, [p.key]: e.target.value })}
                />
              )}
              <span className="text-xs text-slate-500">Slide {p.slideIndex}: {p.context}</span>
            </label>
          ))}
          <button className="rounded bg-blue-600 px-4 py-2 text-white" onClick={onGenerate}>Generate PPTX</button>
        </section>
      )}

      {step === 4 && (
        <section className="rounded bg-white p-6 shadow space-y-3">
          <h2 className="text-xl font-semibold">Done</h2>
          <a href={downloadUrl(jobId)} target="_blank" className="inline-block rounded bg-emerald-600 px-4 py-2 text-white" rel="noreferrer">
            Download Generated PPTX
          </a>
          <p className="text-xs text-slate-500">Note: include header X-API-Token in direct API clients.</p>
        </section>
      )}

      {error && <pre className="rounded bg-red-50 p-3 text-red-700">{error}</pre>}
    </div>
  );
}
