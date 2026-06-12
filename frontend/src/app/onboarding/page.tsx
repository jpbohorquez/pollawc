"use client";

export default function Onboarding() {
  return (
    <div className="min-h-screen bg-gray-50 p-4 font-sans max-w-md mx-auto">
      <header className="py-6 text-center">
        <h1 className="text-3xl font-bold text-green-700">Polla WC26</h1>
        <p className="text-gray-600 mt-2">Guía Maestra del Mundial 2026</p>
      </header>

      <main className="space-y-6">
        <section className="bg-white rounded-xl shadow-md p-6 border-l-4 border-blue-500">
          <h2 className="text-xl font-bold mb-3 flex items-center">
            <span className="mr-2">🎯</span> ¿Cómo Puntuar?
          </h2>
          <p className="text-xs text-blue-600 font-bold mb-4 bg-blue-50 p-2 rounded">
            💡 ¡Ojo! Los puntos valen el DOBLE a partir de la fase de eliminación directa (KO).
          </p>
          <div className="space-y-4 text-sm text-gray-700">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-blue-50 rounded-lg">
                <p className="font-bold text-blue-800">Resultado</p>
                <p className="text-xs">Ganador/Empate</p>
                <div className="flex justify-between mt-1 text-xs">
                  <span>Grupos: <b>5</b></span>
                  <span>KO: <b>10</b></span>
                </div>
              </div>
              <div className="p-3 bg-green-50 rounded-lg">
                <p className="font-bold text-green-800">Goles Exactos</p>
                <p className="text-xs">Por equipo</p>
                <div className="flex justify-between mt-1 text-xs">
                  <span>Grupos: <b>2</b></span>
                  <span>KO: <b>4</b></span>
                </div>
              </div>
              <div className="p-3 bg-orange-50 rounded-lg col-span-2">
                <p className="font-bold text-orange-800">Diferencia de Goles</p>
                <p className="text-xs text-orange-700 italic">Suma solo si aciertas el resultado</p>
                <div className="flex justify-between mt-1 text-xs">
                  <span>Grupos: <b>1</b></span>
                  <span>KO: <b>2</b></span>
                </div>
              </div>
            </div>
            <p className="text-[10px] text-gray-500 text-center">KO = Fase de eliminación directa (Dieciseisavos en adelante)</p>
          </div>
        </section>

        <section className="bg-white rounded-xl shadow-md p-6 border-l-4 border-yellow-500">
          <h2 className="text-xl font-bold mb-3 flex items-center">
            <span className="mr-2">💡</span> Ejemplo Práctico
          </h2>
          <div className="text-sm space-y-3">
            <div className="bg-yellow-50 p-3 rounded-lg border border-yellow-100">
              <p className="font-semibold text-yellow-800 mb-1">Si tu pronóstico es 1 - 0</p>
              <div className="space-y-1 text-xs">
                <p className="flex justify-between"><span>Si el partido termina 1 - 0:</span> <span className="font-bold text-green-600">+10 pts (Pleno)</span></p>
                <p className="flex justify-between"><span>Si el partido termina 2 - 1:</span> <span className="font-bold text-blue-600">+6 pts</span></p>
                <p className="text-[10px] text-gray-500 mt-1">* En fase de grupos. ¡El doble en finales!</p>
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
