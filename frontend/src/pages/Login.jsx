import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Mail, Lock, ShieldCheck } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!email || !password) {
      setError("Please enter your email and password.");
      return;
    }

    setIsLoading(true);

    try {
      const result = await login(email, password);
      
      if (result.success) {
        navigate("/dashboard");
      } else {
        setError(result.error || "Unable to sign in. Please check your credentials.");
      }
    } catch (err) {
      setError("Unable to sign in. Please check your credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSAMLLogin = () => {
    console.log("Redirecting to SAML SSO...");
    navigate("/dashboard");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50/40 to-indigo-50/50 px-4">

      <Card className="w-full max-w-md p-8 bg-white/95 backdrop-blur-sm border border-slate-200/80 rounded-2xl shadow-[0_20px_60px_-15px_rgba(15,23,42,0.15)]">

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-slate-950">
            ChurnAI
          </h1>

          <p className="text-sm font-medium text-blue-600 mt-1">
            Predictive Analytics Platform
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">

          {/* Error */}
          {error && (
            <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {error}
            </div>
          )}

          {/* Email */}
          <div className="space-y-1.5">
            <label
              htmlFor="email"
              className="text-xs font-semibold tracking-wide text-slate-700 uppercase"
            >
              Organization Email
            </label>

            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />

              <Input
                id="email"
                type="email"
                placeholder="name@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="pl-9 h-11 border-slate-300 bg-white text-slate-900 placeholder:text-slate-400 rounded-lg transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
                autoComplete="email"
              />
            </div>
          </div>

          {/* Password */}
          <div className="space-y-1.5">
            <label
              htmlFor="password"
              className="text-xs font-semibold tracking-wide text-slate-700 uppercase"
            >
              Password
            </label>

            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />

              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="pl-9 h-11 border-slate-300 bg-white text-slate-900 placeholder:text-slate-400 rounded-lg transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
                autoComplete="current-password"
              />
            </div>
          </div>

          {/* Remember me / Forgot password */}
          <div className="flex items-center justify-between">

            <div className="flex items-center gap-2">
              <Checkbox
                id="remember"
                checked={rememberMe}
                onCheckedChange={(checked) =>
                  setRememberMe(checked === true)
                }
                className="
                  h-4 w-4
                  rounded-[4px]
                  border-2 border-slate-400
                  bg-white
                  shadow-sm
                  data-[state=checked]:bg-blue-600
                  data-[state=checked]:border-blue-600
                  data-[state=checked]:text-white
                  focus-visible:ring-2
                  focus-visible:ring-blue-500/30
                "
              />

              <label
                htmlFor="remember"
                className="text-sm text-slate-600 cursor-pointer select-none"
              >
                Remember me
              </label>
            </div>

            <a
              href="/forgot-password"
              className="text-sm font-medium text-blue-600 hover:text-blue-700 hover:underline transition-colors"
            >
              Forgot password?
            </a>
          </div>

          {/* Submit */}
          <Button
            type="submit"
            disabled={isLoading}
            className="
              w-full
              h-11
              bg-gradient-to-r from-blue-600 to-indigo-600
              hover:from-blue-700 hover:to-indigo-700
              text-white
              font-semibold
              tracking-wide
              uppercase
              rounded-lg
              shadow-md shadow-blue-600/20
              hover:shadow-lg hover:shadow-blue-600/25
              transition-all
              duration-200
            "
          >
            {isLoading ? "Signing in..." : "Sign In to Dashboard"}
          </Button>
        </form>

        {/* Divider */}
        <div className="flex items-center gap-3 my-6">
          <div className="flex-1 h-px bg-slate-200" />

          <span className="text-xs font-medium text-slate-400 uppercase">
            Or
          </span>

          <div className="flex-1 h-px bg-slate-200" />
        </div>

        {/* SAML */}
        <div className="text-center">
          <p className="text-sm font-medium text-slate-600 mb-3">
            Enterprise Single Sign-On
          </p>

          <Button
            type="button"
            variant="outline"
            onClick={handleSAMLLogin}
            className="
              w-full
              h-11
              flex
              items-center
              justify-center
              gap-2
              font-semibold
              tracking-wide
              uppercase
              rounded-lg
              border-blue-200
              bg-white
              text-blue-700
              hover:bg-blue-50
              hover:border-blue-300
              hover:text-blue-800
              transition-all
              duration-200
            "
          >
            <ShieldCheck className="h-4 w-4 text-blue-600" />
            Login with SAML
          </Button>
        </div>

      </Card>
    </div>
  );
}