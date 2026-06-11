"use client";

export default function Onboarding() {
  return (
    <div className="min-h-screen bg-gray-50 p-4 font-sans max-w-md mx-auto">
      <header className="py-6 text-center">
        <h1 className="text-3xl font-bold text-green-700">Gol Predictor</h1>
        <p className="text-gray-600 mt-2">Guía Maestra del Mundial 2026</p>
      </header>

      <main className="space-y-6">
        <section className="bg-white rounded-xl shadow-md p-6 border-l-4 border-blue-500">
          <h2 className="text-xl font-bold mb-3 flex items-center">
            <span className="mr-2">🎯</span> ¿Cómo Puntuar?
          </h2>
          <div className="space-y-4 text-sm text-gray-700">
            <p>Suma puntos en cada partido según tu puntería:</p>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-blue-50 rounded-lg">
                <p className="font-bold text-blue-800">Resultado</p>
                <p>Acertar Ganador/Empate</p>
                <p className="text-lg font-bold">5 - 10 pts</p>
              </div>
              <div className="p-3 bg-green-50 rounded-lg">
                <p className="font-bold text-green-800">Goles Exactos</p>
                <p>Por cada equipo</p>
                <p className="text-lg font-bold">2 - 4 pts</p>
              </div>
              <div className="p-3 bg-orange-50 rounded-lg col-span-2">
                <p className="font-bold text-orange-800">Diferencia de Goles</p>
                <p>Suma si aciertas la ventaja exacta</p>
                <p className="text-lg font-bold">1 - 2 pts</p>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-white rounded-xl shadow-md p-6 border-l-4 border-red-500">
          <h2 className="text-xl font-bold mb-3 flex items-center">
            <span className="mr-2">⏰</span> Regla de Oro
          </h2>
          <div className="bg-red-50 p-4 rounded-lg text-red-800 text-sm">
            <p className="font-bold">Bloqueo Crítico:</p>
            <p>Tus pronósticos se bloquean estrictamente <span className="font-bold underline">5 minutos antes</span> de que inicie cada partido. ¡No te quedes por fuera!</p>
          </div>
        </section>

        <section className="bg-white rounded-xl shadow-md p-6 border-l-4 border-green-500">
          <h2 className="text-xl font-bold mb-3 flex items-center">
            <span className="mr-2">⚽</span> Pasos para Jugar
          </h2>
          <ol className="list-decimal list-inside space-y-3 text-sm text-gray-700">
            <li><span className="font-bold">Crea o Únete:</span> Ingresa el código de invitación de tu grupo.</li>
            <li><span className="font-bold">Ingresa Marcadores:</span> Ve a la sección de partidos y guarda tus predicciones en lote.</li>
            <li><span className="font-bold">Sigue la Tabla:</span> Mira cómo subes en el ranking tras cada pitazo final.</li>
          </ol>
        </section>
      </main>

      <footer className="mt-8 text-center pb-8">
        <button className="bg-green-600 text-white font-bold py-3 px-8 rounded-full shadow-lg hover:bg-green-700 transition-colors w-full">
          ¡Entendido, vamos a Jugar!
        </button>
      </footer>
    </div>
  );
}
