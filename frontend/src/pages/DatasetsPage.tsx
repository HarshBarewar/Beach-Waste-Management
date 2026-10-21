import React, { useState, useEffect } from 'react';
import { DatasetItem } from '../types';
import { fetchDatasets, uploadDataset } from '../services/api';
import {
  Database,
  Upload,
  Download,
  CheckCircle2,
  AlertCircle,
  FileText,
  Table,
  Check,
  RotateCw
} from 'lucide-react';

export const DatasetsPage: React.FC = () => {
  const [datasets, setDatasets] = useState<DatasetItem[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [datasetName, setDatasetName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const loadDatasets = () => {
    fetchDatasets()
      .then((res) => setDatasets(res.datasets || []))
      .catch((err) => console.error(err));
  };

  useEffect(() => {
    loadDatasets();
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    setError(null);
    setUploadResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    if (datasetName) formData.append('dataset_name', datasetName);

    try {
      const res = await uploadDataset(formData);
      setUploadResult(res);
      setSelectedFile(null);
      setDatasetName('');
      loadDatasets();
    } catch (err: any) {
      setError(err.message || 'Dataset upload and validation failed.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-2">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center space-x-2">
              <Database className="w-5 h-5 text-teal-600" />
              <h2 className="font-bold text-slate-900 text-base">Coastal Dataset Ingestion & Management</h2>
              <span className="text-[10px] font-bold bg-teal-50 text-teal-700 border border-teal-200 px-2 py-0.5 rounded-full">
                Multi-Source Ingestion Pipeline
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Inspect loaded coastal monitoring records, upload new beach waste surveys, or download standardized CSV schema templates.
            </p>
          </div>

          <a
            href="/api/datasets/sample.csv"
            download
            className="inline-flex items-center space-x-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-2 rounded-xl text-xs font-semibold border border-slate-200 transition-colors shrink-0"
          >
            <Download className="w-3.5 h-3.5 text-teal-600" />
            <span>Download Sample CSV Template</span>
          </a>
        </div>
      </div>

      {/* Upload & Current Datasets Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* CSV Uploader Panel */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 text-slate-900 font-bold text-sm border-b border-slate-100 pb-3">
            <Upload className="w-4 h-4 text-teal-600" />
            <span>Upload Beach Waste Dataset</span>
          </div>

          <form onSubmit={handleUpload} className="space-y-3 text-xs">
            <div>
              <label className="block text-slate-600 font-semibold mb-1">Dataset Label / Description</label>
              <input
                type="text"
                placeholder="e.g., California Coastal Cleanup 2024"
                value={datasetName}
                onChange={(e) => setDatasetName(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl font-medium text-slate-800 focus:outline-none focus:border-teal-500"
              />
            </div>

            <div>
              <label className="block text-slate-600 font-semibold mb-1">Select CSV File (.csv)</label>
              <input
                type="file"
                accept=".csv"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                className="w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100 cursor-pointer"
              />
            </div>

            <button
              type="submit"
              disabled={!selectedFile || uploading}
              className="w-full bg-teal-600 hover:bg-teal-700 text-white font-bold py-2.5 rounded-xl text-xs flex items-center justify-center space-x-2 shadow-sm transition-all disabled:opacity-50"
            >
              {uploading ? (
                <>
                  <RotateCw className="w-4 h-4 animate-spin" />
                  <span>Validating & Ingesting...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  <span>Upload & Ingest Dataset</span>
                </>
              )}
            </button>
          </form>

          {uploadResult && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs space-y-1">
              <div className="flex items-center space-x-1 font-bold">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Upload & Validation Successful</span>
              </div>
              <p>Inserted {uploadResult.records_inserted} observations across {uploadResult.beaches_count} beaches.</p>
            </div>
          )}

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Loaded Datasets Table */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
          <h3 className="font-bold text-slate-900 text-sm">Active Datasets in System</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50/70 text-slate-600">
                  <th className="py-2.5 px-3 font-semibold">Dataset Name</th>
                  <th className="py-2.5 px-3 font-semibold">Beaches</th>
                  <th className="py-2.5 px-3 font-semibold text-right">Observations</th>
                  <th className="py-2.5 px-3 font-semibold">Coverage Window</th>
                  <th className="py-2.5 px-3 font-semibold">Status / Quality Flag</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {datasets.map((d) => (
                  <tr key={d.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-2.5 px-3">
                      <div className="font-bold text-slate-800">{d.name}</div>
                      <div className="text-[11px] text-slate-400 font-mono">{d.filename}</div>
                    </td>
                    <td className="py-2.5 px-3 font-semibold text-slate-700">{d.total_beaches} Beaches</td>
                    <td className="py-2.5 px-3 text-right font-extrabold text-teal-700 font-mono">
                      {d.total_rows}
                    </td>
                    <td className="py-2.5 px-3 text-slate-500 text-[11px]">
                      {d.date_range_start} → {d.date_range_end}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                        d.is_synthetic
                          ? 'bg-amber-50 text-amber-800 border-amber-200'
                          : 'bg-emerald-50 text-emerald-800 border-emerald-200'
                      }`}>
                        {d.is_synthetic ? 'SYNTHETIC BENCHMARK' : 'USER VERIFIED'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Schema Field Dictionary */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
        <h3 className="font-bold text-slate-900 text-sm">Standardized Ingestion Schema Specification</h3>
        <p className="text-xs text-slate-500">
          The pipeline validates incoming CSV files against these required and optional observational attributes.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
            <span className="font-bold text-slate-800 block">Core Identifiers</span>
            <code className="text-[11px] text-teal-700 block">observation_id, beach_id, beach_name</code>
            <code className="text-[11px] text-teal-700 block">country, latitude, longitude</code>
            <p className="text-[11px] text-slate-500">Mandatory geolocation and unique key columns.</p>
          </div>

          <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
            <span className="font-bold text-slate-800 block">Waste Quantities</span>
            <code className="text-[11px] text-teal-700 block">waste_mass_kg, waste_mass_unit</code>
            <code className="text-[11px] text-teal-700 block">plastic, metal, glass, paper, organic</code>
            <p className="text-[11px] text-slate-500">Total mass and material composition kilograms.</p>
          </div>

          <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
            <span className="font-bold text-slate-800 block">Covariates & Metadata</span>
            <code className="text-[11px] text-teal-700 block">visitor_count, rainfall_mm, temperature_c</code>
            <code className="text-[11px] text-teal-700 block">surveyed_area_m2, observation_duration_hours</code>
            <p className="text-[11px] text-slate-500">Meteorological and survey normalization metrics.</p>
          </div>
        </div>
      </div>
    </div>
  );
};
