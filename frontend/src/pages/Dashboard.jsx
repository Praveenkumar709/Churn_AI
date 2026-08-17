import { Link, useLocation, useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";

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
  Users as UsersIcon,
  TrendingUp,
  UserX,
  Activity,
} from "lucide-react";

import { uploadApi, reportApi } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import { useState, useEffect } from "react";

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";


/* ============================================================
   NAVIGATION
============================================================ */

const NAV_ITEMS = [
  {
    label: "Dashboard",
    icon: LayoutDashboard,
    path: "/dashboard",
  },
  {
    label: "Customers",
    icon: Users,
    path: "/customers",
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


/* ============================================================
   SIDEBAR
============================================================ */

function Sidebar({ onLogout }) {
  const location = useLocation();

  return (
    <aside className="w-56 shrink-0 border-r border-slate-200/80 bg-white flex flex-col h-screen shadow-[4px_0_20px_-20px_rgba(15,23,42,0.25)]">

      <div className="px-5 py-6">

        <div className="flex items-center gap-2.5">

          <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-md shadow-blue-600/20">
            <Activity className="h-5 w-5 text-white" />
          </div>

          <div>
            <h1 className="text-lg font-bold tracking-tight text-slate-950 leading-none">
              ChurnAI
            </h1>

            <p className="text-[11px] font-medium text-blue-600 mt-1">
              Telecom Analytics
            </p>
          </div>

        </div>

      </div>


      <nav className="flex-1 px-3 mt-2 space-y-1.5">

        {NAV_ITEMS.map(({ label, icon: Icon, path }) => {

          const active =
            location.pathname === path;

          return (
            <Link
              key={label}
              to={path}
              className={`
                group
                flex
                items-center
                gap-3
                px-3
                py-2.5
                rounded-xl
                text-sm
                font-medium
                transition-all
                duration-200
                ${
                  active
                    ? "bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-700 shadow-sm"
                    : "text-slate-500 hover:bg-slate-50 hover:text-slate-800"
                }
              `}
            >

              <Icon
                className={`
                  h-4 w-4
                  ${
                    active
                      ? "text-blue-600"
                      : "text-slate-400 group-hover:text-slate-600"
                  }
                `}
              />

              {label}

              {active && (
                <span className="ml-auto h-1.5 w-1.5 rounded-full bg-blue-600" />
              )}

            </Link>
          );
        })}

      </nav>


      <div className="px-3 pb-5 space-y-1.5">

        <button
          type="button"
          className="w-full group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-500 hover:bg-slate-50 hover:text-slate-800 transition-all"
        >
          <Settings className="h-4 w-4 text-slate-400" />
          Settings
        </button>


        <button
          type="button"
          onClick={onLogout}
          className="w-full group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-500 hover:bg-red-50 hover:text-red-600 transition-all"
        >
          <LogOut className="h-4 w-4 text-slate-400" />
          Logout
        </button>

      </div>

    </aside>
  );
}


/* ============================================================
   TOP BAR
============================================================ */

function TopBar() {

  return (
    <header className="flex items-center justify-between px-8 py-4 border-b border-slate-200/80 bg-white/90 backdrop-blur-md sticky top-0 z-10">

      <div className="relative w-80 max-w-full">

        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />

        <input
          type="text"
          placeholder="Search customers, reports..."
          className="
            w-full
            pl-10
            pr-4
            py-2.5
            text-sm
            rounded-xl
            border
            border-slate-200
            bg-slate-50/70
            text-slate-800
            placeholder:text-slate-400
            focus:outline-none
            focus:border-blue-400
            focus:bg-white
            focus:ring-4
            focus:ring-blue-500/10
          "
        />

      </div>


      <div className="flex items-center gap-2">

        <button
          type="button"
          className="relative h-9 w-9 rounded-xl flex items-center justify-center text-slate-500 hover:bg-slate-50"
        >
          <Bell className="h-5 w-5" />

          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-blue-600 ring-2 ring-white" />
        </button>


        <button
          type="button"
          className="h-9 w-9 rounded-xl flex items-center justify-center text-slate-500 hover:bg-slate-50"
        >
          <HelpCircle className="h-5 w-5" />
        </button>


        <button
          type="button"
          className="h-9 w-9 rounded-xl flex items-center justify-center text-slate-500 hover:bg-blue-50"
        >
          <UserCircle className="h-6 w-6" />
        </button>

      </div>

    </header>
  );
}


/* ============================================================
   STAT CARD
============================================================ */

function StatCard({
  label,
  value,
  icon: Icon,
  iconBg,
  badge,
  badgeTone,
}) {

  return (
    <Card className="
      group
      relative
      overflow-hidden
      p-5
      bg-white
      border
      border-slate-200/80
      rounded-2xl
      shadow-sm
      hover:shadow-lg
      transition-all
    ">

      <div className="relative flex items-start justify-between">

        <span className="text-[11px] font-semibold tracking-wider text-slate-500 uppercase">
          {label}
        </span>


        <div className="flex items-center gap-1.5">

          {badge && (
            <span
              className={`text-[10px] font-semibold px-2 py-1 rounded-full ${badgeTone}`}
            >
              {badge}
            </span>
          )}


          <div
            className={`
              h-9
              w-9
              rounded-xl
              flex
              items-center
              justify-center
              ${iconBg}
            `}
          >
            <Icon className="h-4 w-4" />
          </div>

        </div>

      </div>


      <p className="relative text-2xl font-bold tracking-tight text-slate-950 mt-5">
        {value}
      </p>


      <div className="mt-3 h-1 w-12 rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 opacity-70" />

    </Card>
  );
}


/* ============================================================
   RISK DISTRIBUTION
============================================================ */

function RiskDistributionChart({ data }) {

  return (
    <Card className="
      p-6
      bg-white
      border
      border-slate-200/80
      rounded-2xl
      shadow-sm
    ">

      <div className="mb-4">

        <h3 className="text-sm font-bold text-slate-900">
          Churn Risk Distribution
        </h3>

        <p className="text-xs text-slate-400 mt-1">
          Current AI risk classification
        </p>

      </div>


      <div className="relative h-52">

        <ResponsiveContainer
          width="100%"
          height="100%"
        >

          <PieChart>

            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              innerRadius={55}
              outerRadius={80}
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


            <Tooltip
              formatter={(value, name) => [
                `${value.toLocaleString()} customers`,
                name,
              ]}
            />

          </PieChart>

        </ResponsiveContainer>


        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">

          <span className="text-2xl font-bold text-slate-950">
            {data
              .reduce(
                (sum, item) => sum + item.value,
                0
              )
              .toLocaleString()}
          </span>

          <span className="text-[10px] font-medium text-slate-400">
            Customers
          </span>

        </div>

      </div>


      <div className="mt-4 space-y-3">

        {data.map((item) => (

          <div
            key={item.name}
            className="flex items-center justify-between"
          >

            <span className="flex items-center gap-2 text-sm text-slate-600">

              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{
                  backgroundColor: item.color,
                }}
              />

              {item.name}

            </span>


            <span className="font-semibold text-slate-900">
              {item.value.toLocaleString()}
            </span>

          </div>

        ))}

      </div>

    </Card>
  );
}


/* ============================================================
   CONTRACT DISTRIBUTION
============================================================ */

function ContractDistributionChart({ data }) {

  return (
    <Card className="
      p-6
      bg-white
      border
      border-slate-200/80
      rounded-2xl
      shadow-sm
    ">

      <div className="mb-4">

        <h3 className="text-sm font-bold text-slate-900">
          Contract Distribution
        </h3>

        <p className="text-xs text-slate-400 mt-1">
          Customer distribution by contract type
        </p>

      </div>


      <div className="h-64">

        <ResponsiveContainer
          width="100%"
          height="100%"
        >

          <BarChart
            data={data}
            margin={{
              top: 10,
              right: 10,
              left: -15,
              bottom: 5,
            }}
          >

            <CartesianGrid
              vertical={false}
              stroke="#eef2f7"
            />


            <XAxis
              dataKey="name"
              tickLine={false}
              axisLine={false}
              tick={{
                fontSize: 11,
                fill: "#64748b",
              }}
            />


            <YAxis
              tickLine={false}
              axisLine={false}
              tick={{
                fontSize: 11,
                fill: "#94a3b8",
              }}
            />


            <Tooltip
              formatter={(value) => [
                `${value.toLocaleString()} customers`,
                "Customers",
              ]}
            />


            <Bar
              dataKey="value"
              fill="#2563eb"
              radius={[6, 6, 0, 0]}
            />

          </BarChart>

        </ResponsiveContainer>

      </div>

    </Card>
  );
}


/* ============================================================
   PAYMENT METHOD
============================================================ */

function PaymentMethodChart({ data }) {

  return (
    <Card className="
      p-6
      bg-white
      border
      border-slate-200/80
      rounded-2xl
      shadow-sm
    ">

      <div className="mb-4">

        <h3 className="text-sm font-bold text-slate-900">
          Payment Method
        </h3>

        <p className="text-xs text-slate-400 mt-1">
          Customer distribution by payment method
        </p>

      </div>


      {data.length === 0 ? (

        <div className="py-8 text-center text-sm text-slate-400">
          No payment method data available.
        </div>

      ) : (

        <div className="space-y-4">

          {data.map((item) => (

            <div key={item.name}>

              <div className="flex justify-between mb-1">

                <span className="text-sm text-slate-600">
                  {item.name}
                </span>

                <span className="text-sm font-semibold text-slate-900">
                  {item.value.toLocaleString()}
                </span>

              </div>


              <div className="h-2 bg-slate-100 rounded-full overflow-hidden">

                <div
                  className="h-full bg-blue-600 rounded-full transition-all duration-500"
                  style={{
                    width: `${item.percentage}%`,
                  }}
                />

              </div>

            </div>

          ))}

        </div>

      )}

    </Card>
  );
}


/* ============================================================
   CHURN DRIVERS
============================================================ */

function ChurnDriversChart({ data }) {

  return (
    <Card className="
      p-6
      bg-white
      border
      border-slate-200/80
      rounded-2xl
      shadow-sm
    ">

      <div className="mb-5">

        <h3 className="text-sm font-bold text-slate-900">
          Top Churn Drivers
        </h3>

        <p className="text-xs text-slate-400 mt-1">
          Factors associated with customers predicted to churn
        </p>

      </div>


      {data.length === 0 ? (

        <div className="py-8 text-center text-sm text-slate-400">
          No churn-driver data available.
        </div>

      ) : (

        <div className="space-y-5">

          {data.slice(0, 5).map((item) => {

            const rate = Number(
              item.churn_rate || 0
            );

            const safeRate = Math.max(
              0,
              Math.min(rate, 100)
            );

            return (
              <div key={item.name}>

                <div className="flex items-center justify-between mb-1">

                  <span className="text-sm text-slate-600">
                    {item.name}
                  </span>

                  <span className="text-sm font-semibold text-slate-900">
                    {rate.toFixed(2)}%
                  </span>

                </div>


                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">

                  <div
                    className="h-full bg-blue-600 rounded-full transition-all duration-500"
                    style={{
                      width: `${safeRate}%`,
                    }}
                  />

                </div>


                <p className="text-[11px] text-slate-400 mt-1">

                  {Number(
                    item.affected_customers || 0
                  ).toLocaleString()}

                  {" affected customers • "}

                  {Number(
                    item.churned_customers || 0
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


/* ============================================================
   RETENTION FOCUS
============================================================ */

function RetentionFocus({ data }) {

  return (
    <Card className="
      p-6
      bg-white
      border
      border-slate-200/80
      rounded-2xl
      shadow-sm
    ">

      <div className="mb-5">

        <h3 className="text-sm font-bold text-slate-900">
          Retention Focus
        </h3>

        <p className="text-xs text-slate-400 mt-1">
          Areas that deserve customer-retention attention
        </p>

      </div>


      {data.length === 0 ? (

        <div className="py-8 text-center text-sm text-slate-400">
          No retention recommendations available.
        </div>

      ) : (

        <div className="space-y-4">

          {data.slice(0, 3).map((item, index) => (

            <div
              key={item.name}
              className="flex items-start gap-3"
            >

              <div className="
                h-7
                w-7
                shrink-0
                rounded-lg
                bg-blue-50
                text-blue-600
                flex
                items-center
                justify-center
                text-xs
                font-bold
              ">
                {index + 1}
              </div>


              <div>

                <p className="text-sm font-semibold text-slate-800">
                  Review {item.name.toLowerCase()}
                </p>

                <p className="text-xs text-slate-400 mt-1">
                  {Number(
                    item.churn_rate || 0
                  ).toFixed(2)}
                  % churn rate among affected customers.
                </p>

              </div>

            </div>

          ))}

        </div>

      )}

    </Card>
  );
}


/* ============================================================
   DASHBOARD
============================================================ */

export default function Dashboard() {

  const { logout } = useAuth();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [overviewData, setOverviewData] = useState(null);
  const [summaryData, setSummaryData] = useState(null);


  useEffect(() => {

    const fetchData = async () => {

      try {

        const [overview, summary] =
          await Promise.all([
            uploadApi.getOverview(),
            reportApi.getSummary(),
          ]);

        console.log(
          "Dashboard overview:",
          overview
        );

        console.log(
          "Dashboard summary:",
          summary
        );

        setOverviewData(overview);
        setSummaryData(summary);

      } catch (error) {

        console.error(
          "Failed to fetch dashboard data:",
          error
        );

      } finally {

        setLoading(false);

      }

    };


    fetchData();

  }, []);


  const handleLogout = () => {

    logout();

    navigate("/login");

  };


  /* ============================================================
     STATISTICS
  ============================================================ */

  const totalCustomers =
    overviewData?.total_customers ||
    summaryData?.total_predictions ||
    0;


  const churned =
    overviewData?.churned_customers ??
    summaryData?.churn_count ??
    0;


  const safeCustomers =
    overviewData?.safe_customers ??
    summaryData?.no_churn_count ??
    0;


  const highRisk =
    overviewData?.churn_risk?.high ||
    0;


  const churnRate =
    totalCustomers > 0
      ? (
          (churned / totalCustomers) *
          100
        ).toFixed(1)
      : "0.0";


  const stats = [

    {
      label: "Total Customers",
      value: totalCustomers.toLocaleString(),
      icon: UsersIcon,
      iconBg: "bg-blue-50 text-blue-600",
    },

    {
      label: "At Risk",
      value: highRisk.toLocaleString(),
      icon: TrendingUp,
      badge:
        highRisk > 0
          ? "High"
          : "",
      badgeTone:
        "bg-red-50 text-red-600 border border-red-100",
      iconBg:
        "bg-red-50 text-red-500",
    },

    {
      label: "Churned",
      value: churned.toLocaleString(),
      icon: UserX,
      iconBg:
        "bg-slate-100 text-slate-600",
    },

    {
      label: "Churn Rate",
      value: `${churnRate}%`,
      icon: Activity,
      iconBg:
        "bg-indigo-50 text-indigo-600",
    },

  ];


  /* ============================================================
     RISK DATA
  ============================================================ */

  const riskData = [

    {
      name: "High Risk",
      value:
        overviewData?.churn_risk?.high ||
        0,
      color: "#dc2626",
    },

    {
      name: "Medium Risk",
      value:
        overviewData?.churn_risk?.medium ||
        0,
      color: "#f59e0b",
    },

    {
      name: "Low Risk",
      value:
        overviewData?.churn_risk?.low ||
        0,
      color: "#16a34a",
    },

  ];


  /* ============================================================
     CONTRACT DATA
  ============================================================ */

  const contract =
    overviewData?.churn_by_contract ||
    {};


  const contractData = [

    {
      name: "Month-to-month",
      value:
        contract["Month-to-month"] ||
        0,
    },

    {
      name: "One year",
      value:
        contract["One year"] ||
        0,
    },

    {
      name: "Two year",
      value:
        contract["Two year"] ||
        0,
    },

  ];


  /* ============================================================
     PAYMENT DATA
  ============================================================ */

  const payment =
    overviewData?.churn_by_payment_method ||
    {};


  const paymentTotal =
    Object.values(payment).reduce(
      (sum, value) =>
        sum + Number(value || 0),
      0
    );


  const paymentData = Object.entries(
    payment
  ).map(([name, value]) => ({

    name,

    value: Number(value || 0),

    percentage:
      paymentTotal > 0
        ? Math.round(
            (Number(value || 0) /
              paymentTotal) *
              100
          )
        : 0,

  }));


  /* ============================================================
     CHURN DRIVERS
  ============================================================ */

  const churnDrivers =
    overviewData?.churn_drivers || [];


  /* ============================================================
     LOADING
  ============================================================ */

  if (loading) {

    return (
      <div className="flex h-screen bg-slate-50">

        <Sidebar
          onLogout={handleLogout}
        />

        <div className="flex-1 flex items-center justify-center">

          <div className="text-slate-500">
            Loading dashboard data...
          </div>

        </div>

      </div>
    );
  }


  /* ============================================================
     UI
  ============================================================ */

  return (

    <div className="flex h-screen bg-gradient-to-br from-slate-50 via-blue-50/20 to-indigo-50/30">

      <Sidebar
        onLogout={handleLogout}
      />


      <div className="flex-1 flex flex-col overflow-y-auto">

        <TopBar />


        <main className="p-8 space-y-6">

          {/* Welcome */}

          <div>

            <div className="flex items-center gap-2 mb-2">

              <span className="h-2 w-2 rounded-full bg-emerald-500" />

              <span className="text-xs font-semibold uppercase tracking-wider text-emerald-600">
                System Active
              </span>

            </div>


            <h2 className="text-2xl font-bold tracking-tight text-slate-950">
              Welcome back, Admin
            </h2>


            <p className="text-sm text-slate-500 mt-1">
              Here is the latest data on your customer churn risk.
            </p>

          </div>


          {/* Statistics */}

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

            {stats.map((stat) => (

              <StatCard
                key={stat.label}
                {...stat}
              />

            ))}

          </div>


          {/* Main Charts */}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

            <div className="lg:col-span-1">

              <RiskDistributionChart
                data={riskData}
              />

            </div>


            <div className="lg:col-span-1">

              <ContractDistributionChart
                data={contractData}
              />

            </div>


            <div className="lg:col-span-1">

              <PaymentMethodChart
                data={paymentData}
              />

            </div>

          </div>


          {/* Churn Drivers */}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">

            <ChurnDriversChart
              data={churnDrivers}
            />

            <RetentionFocus
              data={churnDrivers}
            />

          </div>


          {/* Data Information */}

          <Card className="
            p-5
            bg-white
            border
            border-slate-200/80
            rounded-2xl
            shadow-sm
          ">

            <div className="flex items-start gap-3">

              <Activity className="h-5 w-5 text-blue-600 mt-0.5" />

              <div>

                <h3 className="text-sm font-bold text-slate-900">
                  Prediction Model Status
                </h3>

                <p className="text-sm text-slate-500 mt-1">
                  {totalCustomers.toLocaleString()} customer
                  records are currently available for
                  churn-risk analysis.
                </p>

                <p className="text-xs text-slate-400 mt-2">
                  Risk classification is based on the
                  trained machine-learning model.
                </p>

              </div>

            </div>

          </Card>

        </main>

      </div>

    </div>
  );
}