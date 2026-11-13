import React, { useState, useEffect } from 'react';
import {
  DatabaseZap,
  Download,
  FileCode,
  FileSpreadsheet,
  CheckCircle2,
  RefreshCw,
  HardDrive,
  Hash,
} from 'lucide-react';
import { api } from '../services/api';

export const DatasetExports: React.FC = () => {
  const [files, setFiles] = useState<any[]>([]);
  const [manifest, setManifest] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  // Generator trigger state
  const [scale, setScale] = useState('starter');
  const [seed, setSeed] = useState(20261022);
  const [generating, setGenerating] = useState(false);
  const [genStatus, setGenStatus] = useState<any | null>(null);

  const fetchExports = async () => {
    try {
      setLoading(true);
      const res = await api.getExports();
      setFiles(res.files);
      setManifest(res.manifest);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const pollStatus = async () => {
    try {
      const status = await api.getGeneratorStatus();
      setGenStatus(status);
      if (status.status === 'RUNNING') {
        setGenerating(true);
        setTimeout(pollStatus, 2000);
      } else if (generating && (status.status === 'COMPLETED' || status.status === 'FAILED')) {
        setGenerating(false);
        fetchExports();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleTriggerGeneration = async () => {
    try {
      setGenerating(true);
      await api.triggerGenerator(scale, Number(seed), true);
      pollStatus();
    } catch (err: any) {
      alert(`Generation failed to start: ${err.message}`);
      setGenerating(false);
    }
  };

  useEffect(() => {
    fetchExports();
    pollStatus();
  }, []);

  return (
    <div className="space-y-8">
      {/* Generator Control Card */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 shadow-sm space-y-4">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <DatabaseZap className="w-5 h-5 text-indigo-400" /> Synthetic Data Generator Control Center
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Re-generate deterministic synthetic datasets in Starter (~2k carts) or Full (50,000 carts, 20,000 abandoned) scale.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
          <div>
            <label className="text-xs text-slate-400 block mb-1">Execution Mode</label>
            <select
              value={scale}
              onChange={(e) => setScale(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="starter">Starter Scale (2,000 carts, 800 abandoned)</option>
              <option value="full">Full Scale (50,000 carts, 20,000 abandoned)</option>
            </select>
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1">Deterministic Seed</label>
            <input
              type="number"
              value={seed}
              onChange={(e) => setSeed(Number(e.target.value))}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={handleTriggerGeneration}
              disabled={generating}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-semibold shadow-sm shadow-indigo-600/30 transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
              {generating ? 'Generating Dataset...' : 'Run Generation'}
            </button>
          </div>
        </div>

        {genStatus && (
          <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/60 flex items-center justify-between text-xs">
            <span className="text-slate-400">Status: <strong className="text-white">{genStatus.status}</strong></span>
            <span className="text-slate-300 font-mono">{genStatus.message}</span>
          </div>
        )}
      </div>

      {/* Exported Files Directory */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider">
            Available Export Artifacts (CSV, JSON, SQL Seed)
          </h3>
          <button
            onClick={fetchExports}
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Refresh Files
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {loading ? (
            <div className="col-span-full py-12 text-center text-slate-400">Loading export directory...</div>
          ) : files.length === 0 ? (
            <div className="col-span-full py-12 text-center text-slate-400">No export files found.</div>
          ) : (
            files.map((file) => {
              const isCsv = file.filename.endsWith('.csv');
              const isSql = file.filename.endsWith('.sql');
              const Icon = isCsv ? FileSpreadsheet : isSql ? FileCode : HardDrive;
              return (
                <div
                  key={file.filename}
                  className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 hover:border-slate-700 transition-all flex items-center justify-between"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shrink-0">
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <h4 className="font-mono text-xs font-semibold text-white truncate">
                        {file.filename}
                      </h4>
                      <p className="text-[11px] text-slate-400 mt-0.5">
                        {(file.size_bytes / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>

                  <a
                    href={api.getExportFileUrl(file.filename)}
                    download
                    className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white transition-colors shrink-0 ml-2"
                    title="Download File"
                  >
                    <Download className="w-4 h-4" />
                  </a>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Provenance Source Manifest */}
      {manifest && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2.5">
              <Hash className="w-5 h-5 text-indigo-400" />
              <h3 className="font-bold text-white text-base">Provenance Manifest & SHA-256 Checksums</h3>
            </div>
            <span className="text-xs font-mono text-slate-400">Generator v{manifest.generator_version}</span>
          </div>

          <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-300 text-xs font-medium">
            {manifest.synthetic_notice}
          </div>

          <div className="border border-slate-800 rounded-lg overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-800/80 text-slate-400 uppercase">
                <tr>
                  <th className="px-4 py-2.5">Filename</th>
                  <th className="px-4 py-2.5">Row Count</th>
                  <th className="px-4 py-2.5">File Size</th>
                  <th className="px-4 py-2.5">SHA-256 Checksum</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300 font-mono">
                {Object.entries(manifest.files || {}).map(([fname, meta]: [string, any]) => (
                  <tr key={fname} className="hover:bg-slate-800/30">
                    <td className="px-4 py-2.5 text-indigo-400 font-semibold">{fname}</td>
                    <td className="px-4 py-2.5 text-slate-200">{meta.row_count?.toLocaleString()}</td>
                    <td className="px-4 py-2.5 text-slate-400">{(meta.size_bytes / 1024).toFixed(1)} KB</td>
                    <td className="px-4 py-2.5 text-[11px] text-slate-400 truncate max-w-xs">{meta.sha256}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
