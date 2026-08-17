import { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

import {
  LayoutDashboard,
  Users,
  UploadCloud,
  FileBarChart2,
  Settings,
  LogOut,
  Search,
  Bell,
  HelpCircle,
  UserCircle,
  TrendingUp,
  UsersRound,
  UserX,
  Target,
  AlertTriangle,
  Download,
  ShieldCheck,
  Zap,
} from "lucide-react";

import { reportApi, uploadApi } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

/* =========================================================
   NAVIGATION
========================================================= */

const NAV_ITEMS = [
  {
    label: "Dashboard",
    icon: LayoutDashboard,
    path: "/dashboard",
  },
  {
    label: "Customers",
    icon: Users,
    path: "/dashboard",
  },
  {
    label: "Upload",
    icon: UploadCloud,
    path: "/upload",
  },
  {
    label: "Reports",
    icon: FileBarChart2,
    path: "/report",
  },
];

/* =========================================================
   SIDEBAR
========================================================= */

function Sidebar({ onLogout }) {
  const location = useLocation();

  return (
    <aside className="w-56 shrink-0 border-r border-slate-200 bg-white flex flex-col h-screen">

      <div className="px-5 py-5 flex items-center gap-2">

        <div className="h-7 w-7 rounded-lg bg-blue-600 text-white text-xs font-bold flex items-center justify-center">
          C
        </div>

        <div>
          <h1 className="text-sm font-bold text-slate-900 leading-none">
            ChurnAI
          </h1>

          <p className="text-[10px] text-blue-600 mt-0.5">
            Telecom Analytics
          </p>
        </div>

      </div>


      <nav className="flex-1 px-3 mt-2 space-y-1">

        {NAV_ITEMS.map(({ label, icon: Icon, path }) => {

          const active =
            location.pathname === path;

          return (
            <Link
              key={label}
              to={path}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                active
                  ? "bg-blue-50 text-blue-600"
                  : "text-slate-500 hover:bg-slate-50 hover:text-slate-700"
              }`}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          );
        })}

      </nav>


      <div className="px-3 pb-5 space-y-1">

        <button
          type="button"
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-slate-500 hover:bg-slate-50 hover:text-slate-700"
        >
          <Settings className="h-4 w-4" />
          Settings
        </button>


        <button
          type="button"
          onClick={onLogout}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-slate-500 hover:bg-slate-50 hover:text-slate-700"
        >
          <LogOut className="h-4 w-4" />
          Logout
        </button>

      </div>

    </aside>
  );
}


/* =========================================================
   TOP BAR
========================================================= */

function TopBar() {

  return (
    <header className="flex items-center justify-between px-8 py-4 border-b border-slate-200 bg-white">

      <div className="relative w-80 max-w-full">

        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />

        <input
          type="text"
          placeholder="Search customers, reports..."
          className="w-full pl-9 pr-3 py-2 text-sm rounded-lg border border-slate-200 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
        />

      </div>


      <div className="flex items-center gap-4 text-slate-400">

        <Bell className="h-5 w-5 cursor-pointer hover:text-slate-700" />

        <HelpCircle className="h-5 w-5 cursor-pointer hover:text-slate-700" />

        <UserCircle className="h-6 w-6 cursor-pointer hover:text-slate-700" />

      </div>

    </header>
  );
}


/* =========================================================
   SUMMARY CARD
========================================================= */

function SummaryCard({
  label,
  value,
  description,
  icon: Icon,
  iconStyle,
}) {

  return (
    <Card className="p-5 rounded-2xl border border-slate-200 shadow-sm bg-white hover:shadow-md transition-shadow">

      <div className="flex items-start justify-between">

        <div
          className={`h-10 w-10 rounded-xl flex items-center justify-center ${iconStyle}`}
        >
          <Icon className="h-5 w-5" />
        </div>

      </div>


      <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-400 mt-5">
        {label}
      </p>


      <p className="text-2xl font-bold text-slate-900 mt-1">
        {value}
      </p>


      <p className="text-xs text-slate-400 mt-1">
        {description}
      </p>

    </Card>
  );
}


/* =========================================================
   RISK DISTRIBUTION
========================================================= */

function RiskDistribution({ data }) {

  const total =
    data.reduce(
      (sum, item) =>
        sum + Number(item.value || 0),
      0
    );


  const high =
    data.find(
      (item) => item.name === "High Risk"
    )?.value || 0;


  const highPercentage =
    total > 0
      ? ((high / total) * 100).toFixed(1)
      : "0.0";


  return (
    <Card className="p-6 rounded-2xl border border-slate-200 shadow-sm bg-white">

      <div className="flex items-center justify-between mb-4">

        <div>

          <h3 className="text-base font-semibold text-slate-900">
            Customer Risk Distribution
          </h3>

          <p className="text-xs text-slate-400 mt-1">
            Current AI risk classification
          </p>

        </div>

        <Target className="h-5 w-5 text-blue-600" />

      </div>


      <div className="relative h-52">

        {data.length > 0 ? (

          <ResponsiveContainer
            width="100%"
            height="100%"
          >

            <PieChart>

              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                innerRadius={60}
                outerRadius={82}
                startAngle={90}
                endAngle={-270}
                paddingAngle={2}
                stroke="none"
              >

                {data.map((entry) => (

                  <Cell
                    key={entry.name}
                    fill={entry.color}
                  />

                ))}

              </Pie>

              <Tooltip />

            </PieChart>

          </ResponsiveContainer>

        ) : (

          <div className="h-full flex items-center justify-center text-sm text-slate-400">
            No risk data available.
          </div>

        )}


        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">

          <span className="text-2xl font-bold text-slate-900">
            {highPercentage}%
          </span>

          <span className="text-[10px] text-slate-400">
            High Risk
          </span>

        </div>

      </div>


      <div className="space-y-3 mt-2">

        {data.map((item) => (

          <div
            key={item.name}
            className="flex items-center justify-between"
          >

            <div className="flex items-center gap-2">

              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{
                  backgroundColor: item.color,
                }}
              />

              <span className="text-xs text-slate-500">
                {item.name}
              </span>

            </div>


            <span className="text-xs font-semibold text-slate-800">
              {Number(item.value || 0).toLocaleString()}
            </span>

          </div>

        ))}

      </div>

    </Card>
  );
}


/* =========================================================
   CHURN DRIVERS
========================================================= */

function ChurnDrivers({ data }) {

  return (
    <Card className="p-6 rounded-2xl border border-slate-200 shadow-sm bg-white">

      <div className="flex items-center justify-between mb-6">

        <div>

          <h3 className="text-base font-semibold text-slate-900">
            Top Churn Drivers
          </h3>

          <p className="text-xs text-slate-400 mt-1">
            Factors contributing to customer churn
          </p>

        </div>

        <Zap className="h-5 w-5 text-blue-600" />

      </div>


      {data.length === 0 ? (

        <div className="py-8 text-center text-sm text-slate-400">
          No churn-driver data available.
        </div>

      ) : (

        <div className="space-y-5">

          {data.slice(0, 7).map((driver) => {

            const rate =
              Number(driver.churn_rate || 0);


            return (
              <div key={driver.name}>

                <div className="flex items-center justify-between mb-2">

                  <span className="text-sm font-medium text-slate-700">
                    {driver.name}
                  </span>


                  <span className="text-sm font-bold text-slate-900">
                    {rate.toFixed(2)}%
                  </span>

                </div>


                <div className="h-2 rounded-full bg-slate-100 overflow-hidden">

                  <div
                    className="h-full rounded-full bg-blue-600"
                    style={{
                      width: `${Math.min(
                        Math.max(rate, 0),
                        100
                      )}%`,
                    }}
                  />

                </div>


                <p className="text-[11px] text-slate-400 mt-1">

                  {Number(
                    driver.affected_customers || 0
                  ).toLocaleString()}

                  {" affected customers • "}

                  {Number(
                    driver.churned_customers || 0
                  ).toLocaleString()}

                  {" predicted to churn"}

                </p>

              </div>
            );

          })}

        </div>

      )}

    </Card>
  );
}


/* =========================================================
   RETENTION RECOMMENDATIONS
========================================================= */

function Recommendations({ drivers }) {

  const recommendations = drivers
    .slice(0, 3)
    .map((driver) => {

      const name =
        String(driver.name || "customer risk");

      const lower =
        name.toLowerCase();


      let title =
        `Review ${lower}`;


      let description =
        `Prioritize customers affected by ${lower}.`;


      if (lower.includes("late")) {

        title =
          "Address late payments";

        description =
          "Identify customers with repeated late-payment behaviour and offer suitable payment support.";

      } else if (lower.includes("support")) {

        title =
          "Improve support";

        description =
          "Proactively contact customers with repeated support issues.";

      } else if (lower.includes("complaint")) {

        title =
          "Resolve complaints";

        description =
          "Prioritize unresolved complaints and improve resolution follow-up.";

      } else if (lower.includes("bill")) {

        title =
          "Review billing";

        description =
          "Review billing changes and consider suitable plans for affected customers.";

      } else if (lower.includes("tenure")) {

        title =
          "Target new customers";

        description =
          "Focus retention efforts on customers with shorter tenure.";

      }


      return {
        title,
        description,
      };

    });


  return (
    <Card className="rounded-2xl border border-blue-100 bg-blue-50/50 shadow-sm">

      <div className="p-6">

        <div className="flex items-start gap-4">

          <div className="h-10 w-10 rounded-xl bg-blue-600 text-white flex items-center justify-center shrink-0">
            <Zap className="h-5 w-5" />
          </div>


          <div>

            <h3 className="text-base font-semibold text-slate-900">
              AI Retention Recommendations
            </h3>

            <p className="text-xs text-slate-500 mt-1">
              Recommended actions based on current churn patterns.
            </p>

          </div>

        </div>


        {recommendations.length === 0 ? (

          <p className="text-sm text-slate-500 mt-6">
            No recommendations available.
          </p>

        ) : (

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-6">

            {recommendations.map(
              (recommendation, index) => (

                <div
                  key={index}
                  className="rounded-xl border border-white bg-white p-4"
                >

                  <ShieldCheck className="h-4 w-4 text-blue-600" />

                  <p className="text-sm font-semibold text-slate-800 mt-3">
                    {recommendation.title}
                  </p>

                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                    {recommendation.description}
                  </p>

                </div>

              )
            )}

          </div>

        )}

      </div>

    </Card>
  );
}


/* =========================================================
   REPORT PAGE
========================================================= */

export default function Report() {

  const { logout } = useAuth();

  const navigate = useNavigate();

  const [exporting, setExporting] =
    useState(false);

  const [loading, setLoading] =
    useState(true);

  const [overviewData, setOverviewData] =
    useState(null);

  const [summaryData, setSummaryData] =
    useState(null);


  useEffect(() => {

    fetchData();

  }, []);


  const fetchData = async () => {

    try {

      setLoading(true);


      const [
        overview,
        summary,
      ] = await Promise.all([

        uploadApi.getOverview(),

        reportApi.getSummary(),

      ]);


      console.log(
        "Report overview:",
        overview
      );


      console.log(
        "Report summary:",
        summary
      );


      setOverviewData(overview);

      setSummaryData(summary);

    } catch (error) {

      console.error(
        "Failed to fetch report data:",
        error
      );

    } finally {

      setLoading(false);

    }

  };


  const handleLogout = () => {

    logout();

    navigate("/login");

  };


  const handleExport = () => {

    try {

      setExporting(true);


      const total =
        overviewData?.total_customers ||
        summaryData?.total_predictions ||
        0;


      const churnCount =
        summaryData?.churn_count || 0;


      const noChurnCount =
        summaryData?.no_churn_count || 0;


      const averageProbability =
        summaryData?.average_churn_probability ||
        0;


      const highRisk =
        overviewData?.churn_risk?.high || 0;


      const mediumRisk =
        overviewData?.churn_risk?.medium || 0;


      const lowRisk =
        overviewData?.churn_risk?.low || 0;


      const churnRate =
        total > 0
          ? (
              (churnCount / total) *
              100
            ).toFixed(2)
          : "0.00";


      const rows = [

        [
          "Metric",
          "Value",
        ],

        [
          "Total Customers",
          total,
        ],

        [
          "High Risk Customers",
          highRisk,
        ],

        [
          "Medium Risk Customers",
          mediumRisk,
        ],

        [
          "Low Risk Customers",
          lowRisk,
        ],

        [
          "Predicted Churn",
          churnCount,
        ],

        [
          "No Churn",
          noChurnCount,
        ],

        [
          "Churn Rate (%)",
          churnRate,
        ],

        [
          "Average Churn Probability",
          averageProbability,
        ],

      ];


      const csv =
        rows
          .map((row) =>
            row
              .map((value) =>
                `"${String(value).replace(
                  /"/g,
                  '""'
                )}"`
              )
              .join(",")
          )
          .join("\n");


      const blob =
        new Blob(
          [csv],
          {
            type:
              "text/csv;charset=utf-8;",
          }
        );


      const url =
        URL.createObjectURL(blob);


      const link =
        document.createElement("a");


      link.href = url;


      link.download =
        `churn_report_${
          new Date()
            .toISOString()
            .split("T")[0]
        }.csv`;


      document.body.appendChild(link);

      link.click();

      document.body.removeChild(link);

      URL.revokeObjectURL(url);


    } catch (error) {

      console.error(
        "Export failed:",
        error
      );

    } finally {

      setExporting(false);

    }

  };


  /* =========================================================
     REAL VALUES
  ========================================================= */

  const totalCustomers =
    overviewData?.total_customers ??
    summaryData?.total_predictions ??
    0;


  const churnCount =
    summaryData?.churn_count ??
    0;


  const noChurnCount =
    summaryData?.no_churn_count ??
    0;


  const highRisk =
    overviewData?.churn_risk?.high ??
    0;


  const mediumRisk =
    overviewData?.churn_risk?.medium ??
    0;


  const lowRisk =
    overviewData?.churn_risk?.low ??
    0;


  const churnRate =
    totalCustomers > 0
      ? (
          (churnCount /
            totalCustomers) *
          100
        ).toFixed(2)
      : "0.00";


  const averageProbability =
    Number(
      summaryData?.average_churn_probability ||
      0
    );


  const riskData = [

    {
      name: "High Risk",
      value: highRisk,
      color: "#2563eb",
    },

    {
      name: "Medium Risk",
      value: mediumRisk,
      color: "#93c5fd",
    },

    {
      name: "Low Risk",
      value: lowRisk,
      color: "#e2e8f0",
    },

  ];


  const churnDrivers =
    overviewData?.churn_drivers || [];


  /* =========================================================
     LOADING
  ========================================================= */

  if (loading) {

    return (

      <div className="flex h-screen bg-slate-50">

        <Sidebar
          onLogout={handleLogout}
        />


        <div className="flex-1 flex flex-col">

          <TopBar />


          <div className="flex-1 flex items-center justify-center">

            <div className="text-sm text-slate-500">
              Loading report data...
            </div>

          </div>

        </div>

      </div>

    );

  }


  /* =========================================================
     PAGE
  ========================================================= */

  return (

    <div className="flex h-screen bg-slate-50">

      <Sidebar
        onLogout={handleLogout}
      />


      <div className="flex-1 flex flex-col overflow-y-auto">

        <TopBar />


        <main className="p-8 space-y-6 max-w-[1500px] w-full mx-auto">

          {/* PAGE HEADER */}

          <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4">

            <div>

              <div className="flex items-center gap-2 mb-2">

                <FileBarChart2 className="h-4 w-4 text-blue-600" />

                <span className="text-xs font-semibold uppercase tracking-wider text-blue-600">
                  Analytics Report
                </span>

              </div>


              <h2 className="text-2xl font-bold tracking-tight text-slate-900">
                Churn Prediction Report
              </h2>


              <p className="text-sm text-slate-500 mt-1">
                Detailed analysis of customer churn risk and AI predictions.
              </p>

            </div>


            <div className="flex items-center gap-3">

              <div className="hidden sm:flex items-center gap-2 px-3 py-2 rounded-xl bg-emerald-50 border border-emerald-100">

                <ShieldCheck className="h-4 w-4 text-emerald-600" />

                <span className="text-xs font-semibold text-emerald-700">
                  Model Analysis Complete
                </span>

              </div>


              <Button
                onClick={handleExport}
                variant="outline"
                className="rounded-xl h-10"
                disabled={exporting}
              >

                <Download className="h-4 w-4 mr-2" />

                {exporting
                  ? "Exporting..."
                  : "Export Report"}

              </Button>

            </div>

          </div>


          {/* SUMMARY */}

          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">

            <SummaryCard
              label="Customers Analyzed"
              value={totalCustomers.toLocaleString()}
              description="Total records processed"
              icon={UsersRound}
              iconStyle="bg-blue-50 text-blue-600"
            />


            <SummaryCard
              label="High Risk"
              value={highRisk.toLocaleString()}
              description="Customers requiring attention"
              icon={AlertTriangle}
              iconStyle="bg-red-50 text-red-500"
            />


            <SummaryCard
              label="Predicted Churn"
              value={churnCount.toLocaleString()}
              description="Expected customer churn"
              icon={UserX}
              iconStyle="bg-violet-50 text-violet-600"
            />


            <SummaryCard
              label="Overall Churn Rate"
              value={`${churnRate}%`}
              description={`Average probability: ${(averageProbability * 100).toFixed(2)}%`}
              icon={Target}
              iconStyle="bg-emerald-50 text-emerald-600"
            />

          </div>


          {/* RISK DISTRIBUTION */}

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">

            <RiskDistribution
              data={riskData}
            />


            <Card className="p-6 rounded-2xl border border-slate-200 shadow-sm bg-white">

              <div className="mb-6">

                <h3 className="text-base font-semibold text-slate-900">
                  Prediction Summary
                </h3>

                <p className="text-xs text-slate-400 mt-1">
                  Current prediction results
                </p>

              </div>


              <div className="space-y-5">

                <div className="flex items-center justify-between">

                  <span className="text-sm text-slate-500">
                    Total predictions
                  </span>

                  <span className="font-bold text-slate-900">
                    {totalCustomers.toLocaleString()}
                  </span>

                </div>


                <div className="flex items-center justify-between">

                  <span className="text-sm text-slate-500">
                    Predicted churn
                  </span>

                  <span className="font-bold text-red-600">
                    {churnCount.toLocaleString()}
                  </span>

                </div>


                <div className="flex items-center justify-between">

                  <span className="text-sm text-slate-500">
                    Predicted no churn
                  </span>

                  <span className="font-bold text-emerald-600">
                    {noChurnCount.toLocaleString()}
                  </span>

                </div>


                <div className="flex items-center justify-between">

                  <span className="text-sm text-slate-500">
                    Average churn probability
                  </span>

                  <span className="font-bold text-blue-600">
                    {(averageProbability * 100).toFixed(2)}%
                  </span>

                </div>

              </div>

            </Card>

          </div>


          {/* CHURN DRIVERS */}

          <ChurnDrivers
            data={churnDrivers}
          />


          {/* RETENTION */}

          <Recommendations
            drivers={churnDrivers}
          />


          {/* STATUS */}

          <Card className="rounded-2xl border border-slate-200 bg-white shadow-sm">

            <div className="p-6 flex items-start gap-4">

              <ShieldCheck className="h-5 w-5 text-emerald-600 mt-0.5" />

              <div>

                <h3 className="text-sm font-semibold text-slate-900">
                  Prediction Model Status
                </h3>

                <p className="text-sm text-slate-500 mt-1">
                  {totalCustomers.toLocaleString()} customer records are currently available for churn-risk analysis.
                </p>

                <p className="text-xs text-slate-400 mt-2">
                  Risk classification is based on the trained machine-learning model.
                </p>

              </div>

            </div>

          </Card>


          <div className="flex items-center justify-between px-1 pb-4">

            <div className="flex items-center gap-2 text-xs text-slate-400">

              <div className="h-2 w-2 rounded-full bg-emerald-500" />

              Prediction model is ready

            </div>


            <p className="text-xs text-slate-400">
              Data source: current uploaded predictions
            </p>

          </div>

        </main>

      </div>

    </div>

  );
}