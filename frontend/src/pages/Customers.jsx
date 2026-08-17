import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

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
  AlertTriangle,
  RefreshCw,
} from "lucide-react";

import { useAuth } from "../hooks/useAuth";


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


function getRisk(probability) {
  const value = Number(probability || 0);

  if (value >= 0.70) {
    return "High";
  }

  if (value >= 0.40) {
    return "Medium";
  }

  return "Low";
}


function formatProbability(probability) {
  const value = Number(probability || 0);

  if (value <= 1) {
    return `${(value * 100).toFixed(1)}%`;
  }

  return `${value.toFixed(1)}%`;
}


function getReason(customer) {
  if (customer.churn_reason) {
    return customer.churn_reason;
  }

  return "Churn risk identified by ML model";
}


function getRecommendation(customer) {
  if (
    Array.isArray(customer.recommendations) &&
    customer.recommendations.length > 0
  ) {
    return customer.recommendations[0];
  }

  if (
    typeof customer.recommendations === "string" &&
    customer.recommendations.trim()
  ) {
    try {
      const parsed = JSON.parse(
        customer.recommendations
      );

      if (
        Array.isArray(parsed) &&
        parsed.length > 0
      ) {
        return parsed[0];
      }
    } catch {
      return customer.recommendations;
    }
  }

  return "Review customer for retention";
}


function Sidebar({ onLogout }) {
  const location = useLocation();

  return (
    <aside className="w-56 shrink-0 border-r border-slate-200 bg-white flex flex-col h-screen">

      <div className="px-5 py-5 flex items-center gap-2">

        <div className="h-7 w-7 rounded-lg bg-blue-600 text-white text-xs font-bold flex items-center justify-center">
          C
        </div>

        <div>
          <h1 className="text-sm font-bold text-slate-900">
            ChurnAI
          </h1>

          <p className="text-[10px] text-blue-600">
            Telecom Analytics
          </p>
        </div>

      </div>


      <nav className="flex-1 px-3 mt-2 space-y-1">

        {NAV_ITEMS.map(
          ({
            label,
            icon: Icon,
            path,
          }) => {

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
          }
        )}

      </nav>


      <div className="px-3 pb-5 space-y-1">

        <button
          type="button"
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-slate-500 hover:bg-slate-50"
        >
          <Settings className="h-4 w-4" />
          Settings
        </button>


        <button
          type="button"
          onClick={onLogout}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-slate-500 hover:bg-slate-50"
        >
          <LogOut className="h-4 w-4" />
          Logout
        </button>

      </div>

    </aside>
  );
}


function TopBar({
  search,
  setSearch,
}) {
  return (
    <header className="flex items-center justify-between px-8 py-4 border-b border-slate-200 bg-white">

      <div className="relative w-80 max-w-full">

        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />

        <input
          type="text"
          value={search}
          onChange={(event) =>
            setSearch(
              event.target.value
            )
          }
          placeholder="Search customers..."
          className="w-full pl-9 pr-3 py-2 text-sm rounded-lg border border-slate-200 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
        />

      </div>


      <div className="flex items-center gap-4 text-slate-400">

        <Bell className="h-5 w-5" />

        <HelpCircle className="h-5 w-5" />

        <UserCircle className="h-6 w-6" />

      </div>

    </header>
  );
}


export default function Customers() {

  const {
    logout,
  } = useAuth();

  const navigate =
    useNavigate();


  // ==========================================================
  // STATE
  // ==========================================================

  const [customers, setCustomers] =
    useState([]);

  const [totalCustomers, setTotalCustomers] =
    useState(0);

  const [highRiskTotal, setHighRiskTotal] =
    useState(0);

  const [highestProbability, setHighestProbability] =
    useState(0);

  const [totalPages, setTotalPages] =
    useState(1);

  const [loading, setLoading] =
    useState(true);

  const [riskLoading, setRiskLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [search, setSearch] =
    useState("");

  const [page, setPage] =
    useState(1);

  const [limit, setLimit] =
    useState(100);


  // ==========================================================
  // AUTH TOKEN
  // ==========================================================

  const getToken = () => {
    return localStorage.getItem(
      "access_token"
    );
  };


  // ==========================================================
  // LOAD CURRENT PAGE
  // ==========================================================

  const loadCustomers = async (
    requestedPage = page,
    requestedSearch = search
  ) => {

    try {

      setLoading(true);

      setError("");


      const token =
        getToken();


      if (!token) {

        navigate("/login");

        return;
      }


      const params =
        new URLSearchParams();


      params.set(
        "page",
        String(requestedPage)
      );


      params.set(
        "limit",
        String(limit)
      );


      if (
        requestedSearch.trim()
      ) {

        params.set(
          "search",
          requestedSearch.trim()
        );

      }


      const response =
        await fetch(
          `http://127.0.0.1:8000/report/history?${params.toString()}`,
          {
            method: "GET",

            headers: {
              Authorization:
                `Bearer ${token}`,

              "Content-Type":
                "application/json",
            },
          }
        );


      if (response.status === 401) {

        logout();

        navigate("/login");

        return;
      }


      if (!response.ok) {

        const errorText =
          await response.text();

        console.error(
          "Customer API error:",
          errorText
        );

        throw new Error(
          `Failed to load customers (${response.status})`
        );

      }


      const data =
        await response.json();


      if (
        !data ||
        !Array.isArray(
          data.items
        )
      ) {

        throw new Error(
          "Invalid customer data received from server."
        );

      }


      setCustomers(
        data.items
      );


      setTotalCustomers(
        Number(data.total || 0)
      );


      setTotalPages(
        Number(data.total_pages || 1)
      );


    } catch (err) {

      console.error(
        "Customer loading error:",
        err
      );

      setError(
        err.message ||
        "Unable to load customers."
      );

      setCustomers([]);

    } finally {

      setLoading(false);

    }

  };


  // ==========================================================
  // LOAD GLOBAL RISK SUMMARY
  // ==========================================================

  const loadRiskSummary = async () => {

    try {

      setRiskLoading(true);

      const token =
        getToken();


      if (!token) {

        navigate("/login");

        return;
      }


      const response =
        await fetch(
          "http://127.0.0.1:8000/report/risk-summary",
          {
            method: "GET",

            headers: {
              Authorization:
                `Bearer ${token}`,

              "Content-Type":
                "application/json",
            },
          }
        );


      if (response.status === 401) {

        logout();

        navigate("/login");

        return;
      }


      if (!response.ok) {

        const errorText =
          await response.text();

        console.error(
          "Risk summary API error:",
          errorText
        );

        throw new Error(
          `Failed to load risk summary (${response.status})`
        );

      }


      const data =
        await response.json();


      setHighRiskTotal(
        Number(
          data.high_risk || 0
        )
      );


      setHighestProbability(
        Number(
          data.highest_probability || 0
        )
      );


    } catch (err) {

      console.error(
        "Risk summary error:",
        err
      );

      // Do not break the Customers table
      // if only the summary endpoint fails.

    } finally {

      setRiskLoading(false);

    }

  };


  // ==========================================================
  // INITIAL / PAGINATION LOAD
  // ==========================================================

  useEffect(() => {

    loadCustomers(
      page,
      search
    );

  }, [page, limit]);


  // ==========================================================
  // GLOBAL SUMMARY LOAD
  // ==========================================================

  useEffect(() => {

    loadRiskSummary();

  }, []);


  // ==========================================================
  // SEARCH
  // ==========================================================

  useEffect(() => {

    const timer =
      setTimeout(() => {

        setPage(1);

        loadCustomers(
          1,
          search
        );

      }, 400);


    return () =>
      clearTimeout(timer);

  }, [search]);


  // ==========================================================
  // PAGINATION
  // ==========================================================

  const startNumber =
    totalCustomers === 0
      ? 0
      : (page - 1) * limit + 1;


  const endNumber =
    Math.min(
      page * limit,
      totalCustomers
    );


  const previousPage =
    () => {

      if (page > 1) {

        setPage(
          page - 1
        );

      }

    };


  const nextPage =
    () => {

      if (
        page < totalPages
      ) {

        setPage(
          page + 1
        );

      }

    };


  const changeLimit =
    (event) => {

      setLimit(
        Number(
          event.target.value
        )
      );

      setPage(1);

    };


  // ==========================================================
  // REFRESH
  // ==========================================================

  const handleRefresh =
    async () => {

      await Promise.all([
        loadCustomers(
          page,
          search
        ),
        loadRiskSummary(),
      ]);

    };


  // ==========================================================
  // LOGOUT
  // ==========================================================

  const handleLogout =
    () => {

      logout();

      navigate("/login");

    };


  // ==========================================================
  // UI
  // ==========================================================

  return (

    <div className="flex h-screen bg-slate-50">

      <Sidebar
        onLogout={
          handleLogout
        }
      />


      <div className="flex-1 flex flex-col overflow-hidden">

        <TopBar
          search={search}
          setSearch={setSearch}
        />


        <main className="flex-1 overflow-y-auto p-8 max-w-[1600px] w-full mx-auto">


          {/* HEADER */}

          <div className="mb-6 flex items-start justify-between">

            <div>

              <h2 className="text-2xl font-bold text-slate-900">
                Customers
              </h2>

              <p className="text-sm text-slate-500 mt-1">
                Customer churn risk and recommended retention actions.
              </p>

            </div>


            <button
              type="button"
              onClick={
                handleRefresh
              }
              disabled={
                loading ||
                riskLoading
              }
              className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-50"
            >

              <RefreshCw
                className={`h-4 w-4 ${
                  loading ||
                  riskLoading
                    ? "animate-spin"
                    : ""
                }`}
              />

              Refresh

            </button>

          </div>


          {/* ERROR */}

          {error && (

            <div className="mb-6 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">

              {error}

            </div>

          )}


          {/* SUMMARY */}

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">


            {/* TOTAL CUSTOMERS */}

            <div className="bg-white rounded-2xl border border-slate-200 p-5">

              <p className="text-xs text-slate-400">
                Customers Available
              </p>

              <p className="text-2xl font-bold text-slate-900 mt-1">

                {loading
                  ? "..."
                  : totalCustomers.toLocaleString()}

              </p>

            </div>


            {/* HIGH RISK */}

            <div className="bg-white rounded-2xl border border-slate-200 p-5">

              <p className="text-xs text-slate-400">
                High Risk
              </p>

              <p className="text-2xl font-bold text-red-600 mt-1">

                {riskLoading
                  ? "..."
                  : highRiskTotal.toLocaleString()}

              </p>

              {!riskLoading && (
                <p className="text-[10px] text-slate-400 mt-1">
                  Across all customers
                </p>
              )}

            </div>


            {/* HIGHEST PROBABILITY */}

            <div className="bg-white rounded-2xl border border-slate-200 p-5">

              <p className="text-xs text-slate-400">
                Highest Churn Probability
              </p>

              <p className="text-2xl font-bold text-blue-600 mt-1">

                {riskLoading
                  ? "..."
                  : formatProbability(
                      highestProbability
                    )}

              </p>

              {!riskLoading && (
                <p className="text-[10px] text-slate-400 mt-1">
                  Across all customers
                </p>
              )}

            </div>

          </div>


          {/* TABLE */}

          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">


            {/* TABLE HEADER */}

            <div className="p-6 border-b border-slate-100">

              <div className="flex items-center justify-between">

                <div>

                  <h3 className="font-semibold text-slate-900">
                    Customer Risk List
                  </h3>

                  <p className="text-xs text-slate-400 mt-1">
                    Customers ordered by highest predicted churn probability.
                  </p>

                </div>


                <div className="flex items-center gap-2">

                  <span className="text-xs text-slate-400">
                    Rows:
                  </span>

                  <select
                    value={limit}
                    onChange={
                      changeLimit
                    }
                    className="text-sm border border-slate-200 rounded-lg px-2 py-1.5 bg-white"
                  >

                    <option value="50">
                      50
                    </option>

                    <option value="100">
                      100
                    </option>

                    <option value="200">
                      200
                    </option>

                  </select>

                </div>

              </div>

            </div>


            {/* TABLE */}

            <div className="overflow-x-auto">

              <table className="w-full text-left">

                <thead>

                  <tr className="border-b border-slate-100">

                    <th className="px-6 py-4 text-xs text-slate-400">
                      Customer
                    </th>

                    <th className="px-6 py-4 text-xs text-slate-400">
                      Churn Probability
                    </th>

                    <th className="px-6 py-4 text-xs text-slate-400">
                      Risk
                    </th>

                    <th className="px-6 py-4 text-xs text-slate-400">
                      Primary Reason
                    </th>

                    <th className="px-6 py-4 text-xs text-slate-400">
                      Recommended Action
                    </th>

                  </tr>

                </thead>


                <tbody>

                  {loading && (

                    <tr>

                      <td
                        colSpan="5"
                        className="px-6 py-12 text-center text-sm text-slate-400"
                      >

                        <div className="flex flex-col items-center gap-3">

                          <RefreshCw className="h-5 w-5 animate-spin" />

                          Loading customers...

                        </div>

                      </td>

                    </tr>

                  )}


                  {!loading &&
                    customers.length === 0 && (

                      <tr>

                        <td
                          colSpan="5"
                          className="px-6 py-12 text-center text-sm text-slate-400"
                        >

                          No customers found.

                        </td>

                      </tr>

                    )}


                  {!loading &&
                    customers.map(
                      (customer) => {

                        const risk =
                          getRisk(
                            customer.churn_probability
                          );


                        return (

                          <tr
                            key={
                              customer.id ||
                              customer.customer_id
                            }
                            className="border-b border-slate-50 hover:bg-slate-50"
                          >

                            <td className="px-6 py-4 font-semibold text-sm text-slate-800">

                              {
                                customer.customer_id
                              }

                            </td>


                            <td className="px-6 py-4 font-bold text-sm text-slate-900">

                              {
                                formatProbability(
                                  customer.churn_probability
                                )
                              }

                            </td>


                            <td className="px-6 py-4">

                              <span
                                className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold ${
                                  risk === "High"
                                    ? "bg-red-50 text-red-600"
                                    : risk === "Medium"
                                    ? "bg-amber-50 text-amber-600"
                                    : "bg-green-50 text-green-600"
                                }`}
                              >

                                <AlertTriangle className="h-3 w-3" />

                                {risk}

                              </span>

                            </td>


                            <td className="px-6 py-4 text-xs text-slate-500">

                              {
                                getReason(
                                  customer
                                )
                              }

                            </td>


                            <td className="px-6 py-4 text-xs font-semibold text-blue-600">

                              {
                                getRecommendation(
                                  customer
                                )
                              }

                            </td>

                          </tr>

                        );

                      }
                    )}

                </tbody>

              </table>

            </div>


            {/* PAGINATION */}

            {!loading &&
              totalCustomers > 0 && (

                <div className="flex items-center justify-between px-6 py-4 border-t border-slate-100">

                  <p className="text-xs text-slate-400">

                    Showing{" "}

                    {startNumber.toLocaleString()}

                    {"–"}

                    {endNumber.toLocaleString()}

                    {" of "}

                    {totalCustomers.toLocaleString()}

                    {" customers"}

                  </p>


                  <div className="flex items-center gap-2">

                    <button
                      type="button"
                      onClick={
                        previousPage
                      }
                      disabled={
                        page <= 1
                      }
                      className="px-3 py-1.5 text-xs font-medium border border-slate-200 rounded-lg bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
                    >

                      Previous

                    </button>


                    <span className="text-xs text-slate-500 px-2">

                      Page{" "}

                      {page}

                      {" of "}

                      {totalPages}

                    </span>


                    <button
                      type="button"
                      onClick={
                        nextPage
                      }
                      disabled={
                        page >=
                        totalPages
                      }
                      className="px-3 py-1.5 text-xs font-medium border border-slate-200 rounded-lg bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
                    >

                      Next

                    </button>

                  </div>

                </div>

              )}

          </div>

        </main>

      </div>

    </div>

  );
}