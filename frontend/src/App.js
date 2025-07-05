import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [data, setData] = useState({
    insumos: [],
    moldes: [],
    colores: [],
    stats: {}
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState([]);

  useEffect(() => {
    console.log('🚀 React useEffect ejecutándose...');
    loadAllData();
  }, []);

  const loadAllData = async () => {
    console.log('📥 Iniciando loadAllData...');
    setLoading(true);
    setErrors([]);
    
    try {
      // Test de conectividad
      console.log('🌐 Probando conectividad...');
      const healthResponse = await fetch(`${API_BASE_URL}/health`);
      console.log('💚 Health check:', healthResponse.status);

      // Cargar insumos
      console.log('📦 Cargando insumos...');
      const insumosResponse = await fetch(`${API_BASE_URL}/insumos`);
      const insumosData = await insumosResponse.json();
      console.log('✅ Insumos:', insumosData);

      // Cargar moldes  
      const moldesResponse = await fetch(`${API_BASE_URL}/moldes`);
      const moldesData = await moldesResponse.json();
      console.log('🏭 Moldes:', moldesData);

      // Cargar colores
      const coloresResponse = await fetch(`${API_BASE_URL}/colores`);
      const coloresData = await coloresResponse.json();
      console.log('🎨 Colores:', coloresData);

      // Cargar resumen
      const resumenResponse = await fetch(`${API_BASE_URL}/resumen-completo`);
      const resumenData = await resumenResponse.json();
      console.log('📊 Resumen:', resumenData);

      setData({
        insumos: insumosData,
        moldes: moldesData,
        colores: coloresData,
        stats: resumenData
      });

    } catch (error) {
      console.error('❌ Error cargando datos:', error);
      setErrors([error.message]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎨 Vel Arte - Sistema de Gestión</h1>
        <p>Estado: <strong>{loading ? '🔄 Cargando...' : '✅ Completado'}</strong></p>
        
        {errors.length > 0 && (
          <div style={{color: 'red', margin: '10px 0'}}>
            <h3>❌ Errores:</h3>
            {errors.map((error, i) => <p key={i}>{error}</p>)}
          </div>
        )}

        <div style={{display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px', width: '100%', maxWidth: '1200px'}}>
          
          <div style={{background: '#2a2a2a', padding: '20px', borderRadius: '8px'}}>
            <h2>📦 Insumos ({data.insumos.length})</h2>
            <div style={{maxHeight: '200px', overflow: 'auto'}}>
              {data.insumos.map((item, i) => (
                <div key={i} style={{padding: '5px', borderBottom: '1px solid #444'}}>
                  {JSON.stringify(item)}
                </div>
              ))}
            </div>
          </div>

          <div style={{background: '#2a2a2a', padding: '20px', borderRadius: '8px'}}>
            <h2>🏭 Moldes ({data.moldes.length})</h2>
            <div style={{maxHeight: '200px', overflow: 'auto'}}>
              {data.moldes.map((item, i) => (
                <div key={i} style={{padding: '5px', borderBottom: '1px solid #444'}}>
                  {JSON.stringify(item)}
                </div>
              ))}
            </div>
          </div>

          <div style={{background: '#2a2a2a', padding: '20px', borderRadius: '8px'}}>
            <h2>🎨 Colores ({data.colores.length})</h2>
            <div style={{maxHeight: '200px', overflow: 'auto'}}>
              {data.colores.map((item, i) => (
                <div key={i} style={{padding: '5px', borderBottom: '1px solid #444'}}>
                  {JSON.stringify(item)}
                </div>
              ))}
            </div>
          </div>

          <div style={{background: '#2a2a2a', padding: '20px', borderRadius: '8px'}}>
            <h2>📊 Resumen</h2>
            <pre style={{textAlign: 'left', fontSize: '12px'}}>
              {JSON.stringify(data.stats, null, 2)}
            </pre>
          </div>

        </div>

        <div style={{marginTop: '20px'}}>
          <button onClick={loadAllData} style={{padding: '10px 20px', fontSize: '16px'}}>
            🔄 Recargar Datos
          </button>
        </div>
      </header>
    </div>
  );
}

export default App;
