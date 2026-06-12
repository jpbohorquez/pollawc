"use client";

import { useState } from "react";
import { login } from "@/services/api";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(username, password);
      router.push("/onboarding"); // Redirigir después de login
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center p-6 max-w-lg mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-green-700">Polla WC26</h1>
        <p className="text-gray-600">Bienvenido de nuevo</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-2xl shadow-xl space-y-6">
        {error && <p className="text-red-500 text-sm text-center font-medium">{error}</p>}
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Usuario</label>
          <input
            type="text"
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Tu usuario"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
          <input
            type="password"
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
          />
        </div>

        <button
          type="submit"
          className="w-full bg-green-600 text-white font-bold py-3 rounded-lg hover:bg-green-700 transition shadow-md"
        >
          Ingresar
        </button>
        
        <div className="text-center">
          <Link href="/forgot-password" className="text-sm text-gray-500 hover:text-green-600 transition">
            ¿Olvidaste tu contraseña?
          </Link>
        </div>
      </form>

      <p className="mt-8 text-center text-sm text-gray-600">
        ¿No tienes cuenta?{" "}
        <Link href="/register" className="text-green-600 font-bold hover:underline">
          Regístrate aquí
        </Link>
      </p>
    </div>
  );
}
