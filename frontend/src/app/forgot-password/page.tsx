"use client";

import { useState } from "react";
import { apiFetch } from "@/services/api";
import Link from "next/link";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await apiFetch("/forgot-password", {
        method: "POST",
        body: JSON.stringify({ email }),
      });
      setMessage(data.message);
    } catch (err: any) {
      setMessage(`❌ Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center p-6 max-w-lg mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-green-700">Recuperar Acceso</h1>
        <p className="text-gray-600 mt-2 text-sm">Ingresa tu correo para recibir un código de reseteo</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-2xl shadow-xl space-y-6">
        {message && (
          <div className="p-4 bg-blue-50 text-blue-700 text-sm rounded-lg border border-blue-100 font-medium">
            {message}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Correo Electrónico</label>
          <input
            type="email"
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="correo@ejemplo.com"
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-green-600 text-white font-bold py-3 rounded-lg hover:bg-green-700 transition shadow-md disabled:bg-gray-400"
        >
          {loading ? "Enviando..." : "Enviar Código"}
        </button>
      </form>

      <div className="mt-8 text-center space-y-4">
        <Link href="/reset-password" className="block text-green-600 font-bold hover:underline">
          ¿Ya tienes un código? Úsalo aquí
        </Link>
        <Link href="/login" className="block text-gray-500 text-sm hover:underline">
          Volver al Inicio de Sesión
        </Link>
      </div>
    </div>
  );
}
