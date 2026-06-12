"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/services/api";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function ProfilePage() {
  const [profile, setProfile] = useState({
    username: "",
    email: "",
    full_name: "",
    avatar_url: "",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const router = useRouter();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await apiFetch("/users/me");
        setProfile({
          username: data.username,
          email: data.email,
          full_name: data.full_name || "",
          avatar_url: data.avatar_url || "",
        });
      } catch (err) {
        router.push("/login");
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [router]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage("");
    try {
      await apiFetch("/users/me", {
        method: "PUT",
        body: JSON.stringify({
          full_name: profile.full_name,
          email: profile.email,
          avatar_url: profile.avatar_url,
        }),
      });
      setMessage("✅ Perfil actualizado correctamente");
    } catch (err: any) {
      setMessage(`❌ Error: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="p-8 text-center text-green-700 font-bold">Cargando perfil...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-6 max-w-md mx-auto">
      <header className="flex items-center gap-4 mb-8">
        <Link href="/dashboard" className="text-green-700 font-bold">← Volver</Link>
        <h1 className="text-2xl font-bold text-gray-800">Mi Perfil</h1>
      </header>

      <div className="flex flex-col items-center mb-8">
        <div className="w-24 h-24 rounded-full overflow-hidden border-4 border-green-100 shadow-md mb-3 bg-gray-200">
          {profile.avatar_url ? (
            <img src={profile.avatar_url} alt="Avatar" className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-3xl text-gray-400">👤</div>
          )}
        </div>
        <h2 className="text-xl font-bold text-gray-700">@{profile.username}</h2>
      </div>

      <form onSubmit={handleUpdate} className="bg-white p-6 rounded-2xl shadow-md space-y-4">
        {message && (
          <p className={`text-sm text-center font-bold p-2 rounded ${message.includes("✅") ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
            {message}
          </p>
        )}

        <div>
          <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Nombre Completo</label>
          <input
            type="text"
            className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-green-500"
            value={profile.full_name}
            onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
            placeholder="Tu nombre real"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Correo Electrónico</label>
          <input
            type="email"
            className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-green-500"
            value={profile.email}
            onChange={(e) => setProfile({ ...profile, email: e.target.value })}
            placeholder="correo@ejemplo.com"
            required
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-gray-500 uppercase mb-1">URL del Avatar</label>
          <input
            type="text"
            className="w-full p-3 bg-gray-50 border border-gray-200 rounded-lg outline-none focus:ring-2 focus:ring-green-500"
            value={profile.avatar_url}
            onChange={(e) => setProfile({ ...profile, avatar_url: e.target.value })}
            placeholder="https://link-de-tu-imagen.jpg"
          />
        </div>

        <button
          type="submit"
          disabled={saving}
          className="w-full bg-green-600 text-white font-bold py-3 rounded-xl hover:bg-green-700 transition shadow-lg active:scale-95 disabled:bg-gray-400 mt-4"
        >
          {saving ? "Guardando..." : "Actualizar Perfil"}
        </button>
      </form>
      
      <div className="mt-8 text-center">
        <button 
          onClick={() => { localStorage.removeItem("token"); router.push("/login"); }}
          className="text-red-500 font-bold hover:underline"
        >
          Cerrar Sesión
        </button>
      </div>
    </div>
  );
}
