import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  UploadCloud,
  FileSpreadsheet,
  CheckCircle2,
  AlertCircle,
  X,
  ArrowRight,
  Database,
  ShieldCheck,
  FileCheck2,
  Sparkles,
  Clock3,
  Trash2,
} from "lucide-react";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { uploadApi } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";

export default function Upload() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const fileInputRef = useRef(null);

  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  // ============================================================
  // FILE SIZE LIMIT
  // ============================================================

  const MAX_SIZE = 50 * 1024 * 1024;

  // ============================================================
  // DATASET REQUIREMENTS
  // ============================================================

  const requiredFields = [
    "Age",
    "Gender",
    "Dependents",
    "Tenure_Months",
    "Num_Services",
    "Traveler_Profile",
    "Data_Usage_GB",
    "Data_Usage_Change_Pct",
    "Call_Minutes",
    "Num_Calls",
    "SMS_Usage",
    "Usage_5G_4G_Pct",
    "Roaming_Usage_Mins",
    "International_Usage_Mins",
    "Plan_Price",
    "Average_Monthly_Bill",
    "Current_Monthly_Bill",
    "Bill_Change_Pct",
    "Late_Payments",
    "Dropped_Calls",
    "Network_Issues",
    "Downtime_Hours",
    "Complaints",
    "Support_Tickets",
    "Complaint_Resolution_Time_Hrs",
    "Family_Status_*",
    "Location_*",
    "Contract_Type_*",
    "Payment_Method_*",
    "Churn",
  ];

  // ============================================================
  // FILE VALIDATION
  // ============================================================

  const validateFile = (file) => {
    if (!file) {
      return false;
    }

    const extension = file.name.split(".").pop()?.toLowerCase();

    if (!["csv", "xls", "xlsx"].includes(extension)) {
      setError(
        `${file.name} is not supported. Please upload CSV, XLS, or XLSX files.`
      );

      return false;
    }

    if (file.size > MAX_SIZE) {
      setError(
        `${file.name} exceeds the 50 MB file size limit.`
      );

      return false;
    }

    return true;
  };

  // ============================================================
  // ADD FILES
  // ============================================================

  const addFiles = (selectedFiles) => {
    setError("");

    const incomingFiles = Array.from(selectedFiles || []);

    const validFiles = incomingFiles.filter(validateFile);

    if (!validFiles.length) {
      return;
    }

    setFiles((previous) => {
      const existingNames = new Set(
        previous.map((file) => file.name)
      );

      const newFiles = validFiles.filter(
        (file) => !existingNames.has(file.name)
      );

      return [...previous, ...newFiles];
    });
  };

  // ============================================================
  // FILE SELECT
  // ============================================================

  const handleFileSelect = (event) => {
    addFiles(event.target.files);

    event.target.value = "";
  };

  // ============================================================
  // DRAG AND DROP
  // ============================================================

  const handleDrop = (event) => {
    event.preventDefault();

    setIsDragging(false);

    addFiles(event.dataTransfer.files);
  };

  // ============================================================
  // REMOVE FILE
  // ============================================================

  const removeFile = (fileName) => {
    setFiles((previous) =>
      previous.filter(
        (file) => file.name !== fileName
      )
    );
  };

  // ============================================================
  // CLEAR FILES
  // ============================================================

  const clearFiles = () => {
    setFiles([]);
    setError("");
  };

  // ============================================================
  // FORMAT FILE SIZE
  // ============================================================

  const formatSize = (bytes) => {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  // ============================================================
  // GET FILE EXTENSION
  // ============================================================

  const getExtension = (fileName) => {
    return fileName
      .split(".")
      .pop()
      ?.toUpperCase();
  };

  // ============================================================
  // RUN PREDICTIONS
  // ============================================================

  const handleRunPredictions = async () => {
    if (!files.length) {
      setError(
        "Please upload at least one dataset before continuing."
      );

      return;
    }

    setIsUploading(true);
    setError("");

    try {
      const file = files[0];

      const response = await uploadApi.uploadCsv(file);

      if (response) {
        navigate("/report");
      }
    } catch (err) {
      setError(
        err.message ||
          "Failed to upload and process the file. Please try again."
      );
    } finally {
      setIsUploading(false);
    }
  };

  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="flex h-screen bg-slate-50">

      {/* ======================================================
          SIDEBAR
      ====================================================== */}

      <aside className="w-56 shrink-0 border-r border-slate-200 bg-white flex flex-col h-screen">

        <div className="px-5 py-5">
          <h1 className="text-lg font-bold text-slate-900 leading-none">
            ChurnAI
          </h1>

          <p className="text-[11px] text-blue-600 mt-1">
            Telecom Analytics
          </p>
        </div>

        <nav className="flex-1 px-3 mt-2 space-y-1">

          <button
            onClick={() => navigate("/dashboard")}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-slate-500 hover:bg-slate-50"
          >
            Dashboard
          </button>

          <button
            onClick={() => navigate("/dashboard")}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-slate-500 hover:bg-slate-50"
          >
            Customers
          </button>

          <button
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium bg-blue-50 text-blue-600"
          >
            Upload
          </button>

          <button
            onClick={() => navigate("/report")}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-slate-500 hover:bg-slate-50"
          >
            Reports
          </button>

        </nav>

        <div className="px-3 pb-5">

          <button
            onClick={() => {
              logout();
              navigate("/login");
            }}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-slate-500 hover:bg-slate-50"
          >
            Logout
          </button>

        </div>

      </aside>

      {/* ======================================================
          MAIN
      ====================================================== */}

      <div className="flex-1 flex flex-col overflow-y-auto">

        {/* TOP BAR */}

        <header className="h-[73px] shrink-0 flex items-center justify-between px-8 border-b border-slate-200 bg-white">

          <div>

            <p className="text-xs font-medium text-slate-400">
              Data Management
            </p>

            <p className="text-sm font-semibold text-slate-800 mt-0.5">
              Customer Dataset
            </p>

          </div>

          <div className="flex items-center gap-3">

            <div className="hidden md:flex items-center gap-2 px-3 py-2 rounded-xl bg-emerald-50 border border-emerald-100">

              <ShieldCheck className="h-4 w-4 text-emerald-600" />

              <span className="text-xs font-semibold text-emerald-700">
                Secure Processing
              </span>

            </div>

            <div className="h-9 w-9 rounded-xl bg-slate-100 flex items-center justify-center">

              <Database className="h-4 w-4 text-slate-600" />

            </div>

          </div>

        </header>

        {/* ====================================================
            CONTENT
        ==================================================== */}

        <main className="p-8 max-w-7xl w-full mx-auto">

          {/* HEADING */}

          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-7">

            <div>

              <div className="flex items-center gap-2 mb-2">

                <Sparkles className="h-4 w-4 text-blue-600" />

                <span className="text-xs font-semibold uppercase tracking-wider text-blue-600">
                  AI Data Pipeline
                </span>

              </div>

              <h2 className="text-2xl font-bold tracking-tight text-slate-900">
                Upload Customer Data
              </h2>

              <p className="text-sm text-slate-500 mt-1">
                Upload your customer dataset to generate AI-powered churn
                predictions.
              </p>

            </div>

            <div className="flex items-center gap-2 text-xs text-slate-400">

              <Clock3 className="h-4 w-4" />

              Processing usually takes less than a minute

            </div>

          </div>

          {/* MAIN GRID */}

          <div className="grid grid-cols-1 xl:grid-cols-[1fr_310px] gap-6">

            {/* ==================================================
                UPLOAD CARD
            ================================================== */}

            <Card className="rounded-2xl border border-slate-200 shadow-sm bg-white overflow-hidden">

              <div className="p-6 border-b border-slate-100">

                <div className="flex items-start justify-between">

                  <div>

                    <h3 className="text-base font-semibold text-slate-900">
                      Dataset Upload
                    </h3>

                    <p className="text-xs text-slate-400 mt-1">
                      Add one or more customer datasets for analysis.
                    </p>

                  </div>

                  <div className="h-10 w-10 rounded-xl bg-blue-50 flex items-center justify-center">

                    <FileSpreadsheet className="h-5 w-5 text-blue-600" />

                  </div>

                </div>

              </div>

              <div className="p-6">

                {/* DROP ZONE */}

                <div
                  onDragOver={(event) => {
                    event.preventDefault();
                    setIsDragging(true);
                  }}
                  onDragLeave={() => setIsDragging(false)}
                  onDrop={handleDrop}
                  onClick={() =>
                    fileInputRef.current?.click()
                  }
                  className={`relative cursor-pointer rounded-2xl border-2 border-dashed transition-all duration-200 ${
                    isDragging
                      ? "border-blue-500 bg-blue-50 scale-[1.01]"
                      : "border-slate-200 bg-slate-50/60 hover:border-blue-400 hover:bg-blue-50/30"
                  }`}
                >

                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".csv,.xls,.xlsx"
                    className="hidden"
                    onChange={handleFileSelect}
                  />

                  <div className="px-8 py-12 text-center">

                    <div
                      className={`mx-auto h-16 w-16 rounded-2xl flex items-center justify-center transition-transform ${
                        isDragging
                          ? "bg-blue-100 scale-110"
                          : "bg-white border border-slate-200 shadow-sm"
                      }`}
                    >

                      <UploadCloud className="h-7 w-7 text-blue-600" />

                    </div>

                    <h4 className="text-sm font-semibold text-slate-900 mt-5">

                      {isDragging
                        ? "Drop your files here"
                        : "Drag & drop your dataset"}

                    </h4>

                    <p className="text-xs text-slate-400 mt-2">
                      or click anywhere here to browse your computer
                    </p>

                    <div className="flex justify-center items-center gap-2 mt-5">

                      {["CSV", "XLS", "XLSX"].map(
                        (format) => (
                          <span
                            key={format}
                            className="px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-[10px] font-bold text-slate-500"
                          >
                            {format}
                          </span>
                        )
                      )}

                      <span className="text-[10px] text-slate-400 ml-1">
                        Max 50 MB
                      </span>

                    </div>

                  </div>

                </div>

                {/* ERROR */}

                {error && (
                  <div className="mt-4 flex items-start gap-3 p-3.5 rounded-xl bg-red-50 border border-red-100">

                    <AlertCircle className="h-4 w-4 text-red-500 mt-0.5 shrink-0" />

                    <p className="text-xs text-red-600 leading-relaxed">
                      {error}
                    </p>

                  </div>
                )}

                {/* SELECTED FILES */}

                {files.length > 0 && (

                  <div className="mt-6">

                    <div className="flex items-center justify-between mb-3">

                      <div>

                        <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                          Selected Files
                        </p>

                        <p className="text-sm font-semibold text-slate-800 mt-1">
                          {files.length}{" "}
                          {files.length === 1
                            ? "file"
                            : "files"}{" "}
                          ready
                        </p>

                      </div>

                      <button
                        onClick={clearFiles}
                        className="flex items-center gap-1.5 text-xs font-medium text-slate-400 hover:text-red-500 transition-colors"
                      >

                        <Trash2 className="h-3.5 w-3.5" />

                        Clear all

                      </button>

                    </div>

                    <div className="space-y-2">

                      {files.map((file) => (

                        <div
                          key={file.name}
                          className="group flex items-center justify-between p-3.5 rounded-xl border border-slate-200 bg-white hover:border-blue-200 hover:bg-blue-50/20 transition-all"
                        >

                          <div className="flex items-center gap-3 min-w-0">

                            <div className="h-10 w-10 shrink-0 rounded-xl bg-blue-50 flex items-center justify-center">

                              <FileSpreadsheet className="h-5 w-5 text-blue-600" />

                            </div>

                            <div className="min-w-0">

                              <p className="text-sm font-medium text-slate-800 truncate">
                                {file.name}
                              </p>

                              <div className="flex items-center gap-2 mt-1">

                                <span className="text-[10px] font-semibold text-slate-400">
                                  {getExtension(file.name)}
                                </span>

                                <span className="text-slate-300">
                                  •
                                </span>

                                <span className="text-[10px] text-slate-400">
                                  {formatSize(file.size)}
                                </span>

                                <span className="text-slate-300">
                                  •
                                </span>

                                <span className="flex items-center gap-1 text-[10px] font-medium text-emerald-600">

                                  <CheckCircle2 className="h-3 w-3" />

                                  Ready

                                </span>

                              </div>

                            </div>

                          </div>

                          <button
                            onClick={(event) => {
                              event.stopPropagation();
                              removeFile(file.name);
                            }}
                            className="h-8 w-8 shrink-0 rounded-lg flex items-center justify-center text-slate-300 hover:bg-red-50 hover:text-red-500 transition-colors"
                          >

                            <X className="h-4 w-4" />

                          </button>

                        </div>

                      ))}

                    </div>

                  </div>

                )}

                {/* BOTTOM ACTION */}

                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mt-7 pt-5 border-t border-slate-100">

                  <div className="flex items-center gap-2">

                    <FileCheck2 className="h-4 w-4 text-emerald-600" />

                    <span className="text-xs text-slate-500">
                      Your dataset will be validated before prediction.
                    </span>

                  </div>

                  <Button
                    onClick={handleRunPredictions}
                    disabled={
                      !files.length ||
                      isUploading
                    }
                    className="rounded-xl bg-blue-600 hover:bg-blue-700 text-white px-6 h-10 font-semibold shadow-sm disabled:opacity-50"
                  >

                    {isUploading
                      ? "Processing..."
                      : "Run Predictions"}

                    <ArrowRight className="h-4 w-4 ml-2" />

                  </Button>

                </div>

              </div>

            </Card>

            {/* ==================================================
                REQUIREMENTS CARD
            ================================================== */}

            <Card className="rounded-2xl border border-slate-200 shadow-sm bg-white h-fit">

              <div className="p-6">

                <div className="flex items-start justify-between">

                  <div>

                    <h3 className="text-base font-semibold text-slate-900">
                      Dataset Requirements
                    </h3>

                    <p className="text-xs text-slate-400 mt-1">
                      Required fields for prediction
                    </p>

                  </div>

                  <div className="h-9 w-9 rounded-xl bg-emerald-50 flex items-center justify-center">

                    <ShieldCheck className="h-4 w-4 text-emerald-600" />

                  </div>

                </div>

                <div className="space-y-3 mt-6">

                  {requiredFields.map(
                    (item) => (

                      <div
                        key={item}
                        className="flex items-center gap-3"
                      >

                        <div className="h-6 w-6 rounded-lg bg-emerald-50 flex items-center justify-center shrink-0">

                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />

                        </div>

                        <span className="text-sm text-slate-600">
                          {item}
                        </span>

                      </div>

                    )
                  )}

                </div>

                <div className="mt-6 pt-5 border-t border-slate-100">

                  <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Supported formats
                  </p>

                  <p className="text-xs text-slate-500 mt-2 leading-relaxed">
                    CSV, XLS and XLSX files up to 50 MB are supported.
                  </p>

                </div>

              </div>

            </Card>

          </div>

          {/* ====================================================
              PROCESSING INFORMATION
          ==================================================== */}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">

            <div className="rounded-2xl border border-slate-200 bg-white p-5">

              <div className="h-9 w-9 rounded-xl bg-blue-50 flex items-center justify-center">

                <Database className="h-4 w-4 text-blue-600" />

              </div>

              <p className="text-sm font-semibold text-slate-800 mt-4">
                Data Validation
              </p>

              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                We check columns, missing values and invalid records before
                prediction.
              </p>

            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-5">

              <div className="h-9 w-9 rounded-xl bg-violet-50 flex items-center justify-center">

                <Sparkles className="h-4 w-4 text-violet-600" />

              </div>

              <p className="text-sm font-semibold text-slate-800 mt-4">
                AI Prediction
              </p>

              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                Your customer data is analyzed using the Logistic Regression
                churn prediction model.
              </p>

            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-5">

              <div className="h-9 w-9 rounded-xl bg-emerald-50 flex items-center justify-center">

                <CheckCircle2 className="h-4 w-4 text-emerald-600" />

              </div>

              <p className="text-sm font-semibold text-slate-800 mt-4">
                Actionable Results
              </p>

              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                View customer risk scores and insights on the dashboard and
                reports.
              </p>

            </div>

          </div>

        </main>

      </div>

    </div>
  );
}