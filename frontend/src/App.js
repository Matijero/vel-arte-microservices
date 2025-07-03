import React, { useState, useEffect } from 'react';
import './App.css';

// Configuración de la API
const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [data, setData] = useState({
    insumos: [],
    moldes: [],
    colores: [],
    stats: {}
  });
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('');
  const [editingItem, setEditingItem] = useState(null);

  // Cargar datos iniciales
  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [insumosRes, moldesRes, coloresRes, statsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/insumos`),
        fetch(`${API_BASE_URL}/moldes`),
        fetch(`${API_BASE_URL}/colores`),
        fetch(`${API_BASE_URL}/resumen-completo`)
      ]);

      const insumos = await insumosRes.json();
      const moldes = await moldesRes.json();
      const colores = await coloresRes.json();
      const stats = await statsRes.json();

      setData({
        insumos: insumos.insumos || [],
        moldes: moldes.moldes || [],
        colores: colores.colores || [],
        stats
      });

      showNotification('✅ Datos cargados correctamente');
    } catch (error) {
      console.error('Error cargando datos:', error);
      showNotification('❌ Error cargando datos');
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (message) => {
    setNotification(message);
    setTimeout(() => setNotification(''), 4000);
  };

  const openModal = (type, item = null) => {
    setModalType(type);
    setEditingItem(item);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setModalType('');
    setEditingItem(null);
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="container">
          <h1>🕯️ Sistema Vel Arte - Completo y Funcional</h1>
          <div className="header-actions">
            <span className="status-badge">🟢 Backend Conectado</span>
            <button onClick={loadAllData} className="btn-refresh">
              🔄 Actualizar
            </button>
          </div>
        </div>
      </header>

      {/* Loading bar */}
      {loading && <div className="loading-bar"></div>}

      {/* Notification */}
      {notification && (
        <div className="notification">
          {notification}
        </div>
      )}

      {/* Navigation */}
      <nav className="nav-tabs">
        <div className="container">
          <button 
            className={`tab ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 Dashboard
          </button>
          <button 
            className={`tab ${activeTab === 'insumos' ? 'active' : ''}`}
            onClick={() => setActiveTab('insumos')}
          >
            📦 Insumos ({data.insumos.length})
          </button>
          <button 
            className={`tab ${activeTab === 'moldes' ? 'active' : ''}`}
            onClick={() => setActiveTab('moldes')}
          >
            🏺 Moldes ({data.moldes.length})
          </button>
          <button 
            className={`tab ${activeTab === 'colores' ? 'active' : ''}`}
            onClick={() => setActiveTab('colores')}
          >
            🎨 Colores ({data.colores.length})
          </button>
          <button 
            className={`tab ${activeTab === 'calculadora' ? 'active' : ''}`}
            onClick={() => setActiveTab('calculadora')}
          >
            🧮 Calculadora ⭐
          </button>
        </div>
      </nav>

      {/* Content */}
      <main className="main-content">
        <div className="container">
          {activeTab === 'dashboard' && <Dashboard data={data} />}
          {activeTab === 'insumos' && (
            <Insumos 
              data={data} 
              onRefresh={loadAllData} 
              showNotification={showNotification}
              onAdd={() => openModal('add-insumo')}
              onEdit={(insumo) => openModal('edit-insumo', insumo)}
            />
          )}
          {activeTab === 'moldes' && (
            <Moldes 
              data={data} 
              onRefresh={loadAllData} 
              showNotification={showNotification}
              onAdd={() => openModal('add-molde')}
              onEdit={(molde) => openModal('edit-molde', molde)}
            />
          )}
          {activeTab === 'colores' && (
            <Colores 
              data={data} 
              onRefresh={loadAllData} 
              showNotification={showNotification}
              onAdd={() => openModal('add-color')}
            />
          )}
          {activeTab === 'calculadora' && (
            <CalculadoraFuncional 
              data={data} 
              showNotification={showNotification} 
            />
          )}
        </div>
      </main>

      {/* Modal */}
      {showModal && (
        <Modal 
          type={modalType}
          item={editingItem}
          onClose={closeModal}
          onSuccess={() => {
            closeModal();
            loadAllData();
          }}
          showNotification={showNotification}
        />
      )}
    </div>
  );
}

// Dashboard Component (igual que antes)
function Dashboard({ data }) {
  const { stats } = data;
  const resumen = stats['📊 resumen_general'] || {};

  return (
    <div className="dashboard">
      <h2>📊 Dashboard Principal</h2>
      
      <div className="stats-grid">
        <div className="stat-card insumos">
          <div className="stat-icon">📦</div>
          <div className="stat-number">{resumen.total_insumos || 0}</div>
          <div className="stat-label">Insumos Totales</div>
        </div>
        
        <div className="stat-card moldes">
          <div className="stat-icon">🏺</div>
          <div className="stat-number">{resumen.total_moldes || 0}</div>
          <div className="stat-label">Moldes Disponibles</div>
        </div>
        
        <div className="stat-card colores">
          <div className="stat-icon">🎨</div>
          <div className="stat-number">{resumen.total_colores || 0}</div>
          <div className="stat-label">Colores Disponibles</div>
        </div>
      </div>

      <div className="info-grid">
        <div className="info-card">
          <h3>💰 Información Financiera</h3>
          <p><strong>Valor Aproximado Inventario:</strong></p>
          <p className="value">${(stats['💰 valor_aproximado_inventario'] || 0).toLocaleString()}</p>
        </div>
        
        <div className="info-card">
          <h3>📈 Destacados</h3>
          <p><strong>Molde más caro:</strong> {stats['📈 estadisticas']?.molde_mas_caro || 'N/A'}</p>
          <p><strong>Mayor stock:</strong> {stats['📈 estadisticas']?.mayor_stock || 'N/A'}</p>
        </div>
      </div>

      <div className="charts-info">
        <h3>📈 Distribución de Datos</h3>
        <div className="distribution-grid">
          {Object.entries(stats['📦 insumos_por_tipo'] || {}).map(([tipo, cantidad]) => (
            <div key={tipo} className="distribution-item">
              <span className="tipo">{tipo}</span>
              <span className="cantidad">{cantidad}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Insumos Component con funcionalidad completa
function Insumos({ data, onRefresh, showNotification, onAdd, onEdit }) {
  const [filtroTipo, setFiltroTipo] = useState('');
  const [busqueda, setBusqueda] = useState('');

  const insumosFiltrados = data.insumos.filter(insumo => {
    const matchTipo = !filtroTipo || insumo.tipo === filtroTipo;
    const matchBusqueda = !busqueda || 
      insumo.descripcion.toLowerCase().includes(busqueda.toLowerCase()) ||
      insumo.codigo.toLowerCase().includes(busqueda.toLowerCase());
    return matchTipo && matchBusqueda;
  });

  const tiposUnicos = [...new Set(data.insumos.map(i => i.tipo))];

  const eliminarInsumo = async (codigo) => {
    if (window.confirm(`¿Estás seguro de eliminar el insumo ${codigo}?`)) {
      try {
        const response = await fetch(`${API_BASE_URL}/insumos/${codigo}`, {
          method: 'DELETE'
        });
        
        if (response.ok) {
          showNotification(`✅ Insumo ${codigo} eliminado correctamente`);
          onRefresh();
        } else {
          const error = await response.json();
          showNotification(`❌ Error: ${error.detail}`);
        }
      } catch (error) {
        showNotification('❌ Error eliminando insumo');
      }
    }
  };

  return (
    <div className="insumos">
      <h2>📦 Gestión de Insumos</h2>
      
      <div className="filters-card">
        <div className="filters-grid">
          <div className="filter-group">
            <label>🔍 Buscar insumo:</label>
            <input
              type="text"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              placeholder="Buscar por código o descripción..."
              className="search-input"
            />
          </div>
          
          <div className="filter-group">
            <label>📋 Filtrar por tipo:</label>
            <select
              value={filtroTipo}
              onChange={(e) => setFiltroTipo(e.target.value)}
              className="filter-select"
            >
              <option value="">Todos los tipos</option>
              {tiposUnicos.map(tipo => (
                <option key={tipo} value={tipo}>{tipo}</option>
              ))}
            </select>
          </div>
          
          <div className="filter-group">
            <button className="btn-primary" onClick={onAdd}>
              ➕ Agregar Insumo
            </button>
          </div>
        </div>
        
        <div className="filter-info">
          <strong>Mostrando {insumosFiltrados.length} de {data.insumos.length} insumos</strong>
        </div>
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Código</th>
              <th>Descripción</th>
              <th>Tipo</th>
              <th>Costo Base</th>
              <th>Stock</th>
              <th>Proveedor</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {insumosFiltrados.map((insumo) => (
              <tr key={insumo.codigo}>
                <td><strong>{insumo.codigo}</strong></td>
                <td>{insumo.descripcion}</td>
                <td>
                  <span className={`badge badge-${insumo.tipo}`}>
                    {insumo.tipo}
                  </span>
                </td>
                <td>
                  <span className="price">
                    ${insumo.costo_base?.toLocaleString()}
                  </span>
                </td>
                <td>
                  <span className={`stock ${insumo.cantidad_inventario <= 10 ? 'low' : 'good'}`}>
                    {insumo.cantidad_inventario} {insumo.unidad_medida}
                  </span>
                </td>
                <td>
                  <small>{insumo.proveedor || 'Sin proveedor'}</small>
                </td>
                <td>
                  <div className="actions">
                    <button 
                      className="btn-edit" 
                      onClick={() => onEdit(insumo)}
                      title="Editar"
                    >
                      ✏️
                    </button>
                    <button 
                      className="btn-delete"
                      onClick={() => eliminarInsumo(insumo.codigo)}
                      title="Eliminar"
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Moldes Component con funcionalidad completa
function Moldes({ data, onRefresh, showNotification, onAdd, onEdit }) {
  const [filtroEstado, setFiltroEstado] = useState('');
  const [busqueda, setBusqueda] = useState('');

  const moldesFiltrados = data.moldes.filter(molde => {
    const matchEstado = !filtroEstado || molde.estado === filtroEstado;
    const matchBusqueda = !busqueda || 
      molde.descripcion.toLowerCase().includes(busqueda.toLowerCase()) ||
      molde.codigo.toLowerCase().includes(busqueda.toLowerCase());
    return matchEstado && matchBusqueda;
  });

  const estadosUnicos = [...new Set(data.moldes.map(m => m.estado))];

  return (
    <div className="moldes">
      <h2>🏺 Gestión de Moldes</h2>
      
      <div className="filters-card">
        <div className="filters-grid">
          <div className="filter-group">
            <label>🔍 Buscar molde:</label>
            <input
              type="text"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              placeholder="Buscar por código o descripción..."
              className="search-input"
            />
          </div>
          
          <div className="filter-group">
            <label>📋 Filtrar por estado:</label>
            <select
              value={filtroEstado}
              onChange={(e) => setFiltroEstado(e.target.value)}
              className="filter-select"
            >
              <option value="">Todos los estados</option>
              {estadosUnicos.map(estado => (
                <option key={estado} value={estado}>{estado}</option>
              ))}
            </select>
          </div>
          
          <div className="filter-group">
            <button className="btn-primary" onClick={onAdd}>
              ➕ Agregar Molde
            </button>
          </div>
        </div>
        
        <div className="filter-info">
          <strong>Mostrando {moldesFiltrados.length} de {data.moldes.length} moldes</strong>
        </div>
      </div>

      <div className="moldes-grid">
        {moldesFiltrados.map((molde) => (
          <div key={molde.codigo} className="molde-card">
            <div className="molde-header">
              <h3>{molde.codigo}</h3>
              <span className={`status status-${molde.estado}`}>
                {molde.estado}
              </span>
            </div>
            
            <div className="molde-content">
              <h4>{molde.descripcion}</h4>
              
              <div className="molde-details">
                <p><strong>Dimensiones:</strong> {molde.dimensiones || 'N/A'}</p>
                <p><strong>Peso cera:</strong> {molde.peso_cera_necesario}g</p>
                <p><strong>Pabilo:</strong> {molde.cantidad_pabilo} unidades</p>
                {molde.ubicacion_fisica && (
                  <p><strong>Ubicación:</strong> {molde.ubicacion_fisica}</p>
                )}
              </div>

              {molde.precio_base_calculado && (
                <div className="molde-price">
                  ${molde.precio_base_calculado.toLocaleString()}
                </div>
              )}
            </div>
            
            <div className="molde-actions">
              <button onClick={() => onEdit(molde)}>✏️ Editar</button>
              <button className="btn-delete">🗑️ Eliminar</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Colores Component
function Colores({ data, onRefresh, showNotification, onAdd }) {
  return (
    <div className="colores">
      <h2>🎨 Gestión de Colores</h2>
      
      <div className="section-header">
        <button className="btn-primary" onClick={onAdd}>
          ➕ Agregar Color
        </button>
      </div>

      <div className="colores-grid">
        {data.colores.map((color) => (
          <div key={color.codigo} className="color-card">
            <div className="color-preview">
              <div 
                className="color-circle"
                style={{ backgroundColor: getColorByName(color.nombre) }}
              ></div>
            </div>
            
            <div className="color-info">
              <h3>{color.codigo}</h3>
              <p>{color.nombre}</p>
              <small>Gotas estándar: {color.cantidad_gotas_estandar}</small>
            </div>
            
            <div className="color-actions">
              <button className="btn-edit">✏️</button>
              <button className="btn-delete">🗑️</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ⭐ CALCULADORA FUNCIONAL ⭐
function CalculadoraFuncional({ data, showNotification }) {
  const [moldeSeleccionado, setMoldeSeleccionado] = useState('');
  const [insumosSeleccionados, setInsumosSeleccionados] = useState({});
  const [coloresSeleccionados, setColoresSeleccionados] = useState([]);
  const [nivelCalidad, setNivelCalidad] = useState(2);
  const [cantidadProducir, setCantidadProducir] = useState(1);
  const [margenAdicional, setMargenAdicional] = useState(0);
  const [resultado, setResultado] = useState(null);
  const [calculando, setCalculando] = useState(false);

  const calcularCosto = async () => {
    if (!moldeSeleccionado) {
      showNotification('❌ Selecciona un molde para calcular');
      return;
    }

    if (Object.keys(insumosSeleccionados).length === 0) {
      showNotification('❌ Agrega al menos un insumo');
      return;
    }

    setCalculando(true);
    try {
      const requestData = {
        molde_codigo: moldeSeleccionado,
        insumos: insumosSeleccionados,
        colores: coloresSeleccionados,
        nivel_calidad: nivelCalidad,
        cantidad_producir: cantidadProducir,
        margen_adicional: margenAdicional
      };

      const response = await fetch(`${API_BASE_URL}/calcular-costo`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      if (response.ok) {
        const result = await response.json();
        setResultado(result);
        showNotification('✅ Cálculo realizado correctamente');
      } else {
        const error = await response.json();
        showNotification(`❌ Error en cálculo: ${error.detail}`);
      }
    } catch (error) {
      showNotification('❌ Error conectando con el servidor');
    } finally {
      setCalculando(false);
    }
  };

  const agregarInsumo = (codigo) => {
    setInsumosSeleccionados({
      ...insumosSeleccionados,
      [codigo]: 1
    });
  };

  const actualizarCantidadInsumo = (codigo, cantidad) => {
    if (cantidad <= 0) {
      const nuevosInsumos = { ...insumosSeleccionados };
      delete nuevosInsumos[codigo];
      setInsumosSeleccionados(nuevosInsumos);
    } else {
      setInsumosSeleccionados({
        ...insumosSeleccionados,
        [codigo]: parseFloat(cantidad)
      });
    }
  };

  const toggleColor = (codigo) => {
    if (coloresSeleccionados.includes(codigo)) {
      setColoresSeleccionados(coloresSeleccionados.filter(c => c !== codigo));
    } else {
      setColoresSeleccionados([...coloresSeleccionados, codigo]);
    }
  };

  return (
    <div className="calculadora">
      <h2>🧮 Calculadora de Costos ⭐ FUNCIONAL ⭐</h2>
      
      <div className="calculator-grid">
        <div className="calculator-inputs">
          <div className="input-group">
            <label>🏺 Seleccionar Molde:</label>
            <select
              value={moldeSeleccionado}
              onChange={(e) => setMoldeSeleccionado(e.target.value)}
              className="molde-select"
            >
              <option value="">Selecciona un molde...</option>
              {data.moldes.map(molde => (
                <option key={molde.codigo} value={molde.codigo}>
                  {molde.codigo} - {molde.descripcion}
                </option>
              ))}
            </select>
          </div>

          <div className="input-group">
            <label>📦 Agregar Insumos:</label>
            <select 
              onChange={(e) => {
                if (e.target.value) {
                  agregarInsumo(e.target.value);
                  e.target.value = '';
                }
              }}
              className="molde-select"
            >
              <option value="">Selecciona insumo para agregar...</option>
              {data.insumos.map(insumo => (
                <option key={insumo.codigo} value={insumo.codigo}>
                  {insumo.codigo} - {insumo.descripcion}
                </option>
              ))}
            </select>
          </div>

          <div className="insumos-section">
            <h3>📋 Insumos Seleccionados</h3>
            {Object.keys(insumosSeleccionados).length === 0 ? (
              <p className="empty-state">No hay insumos seleccionados</p>
            ) : (
              Object.entries(insumosSeleccionados).map(([codigo, cantidad]) => {
                const insumo = data.insumos.find(i => i.codigo === codigo);
                return (
                  <div key={codigo} className="insumo-input">
                    <div className="insumo-header">
                      <strong>{insumo?.descripcion || codigo}</strong>
                      <small>{codigo}</small>
                    </div>
                    <div className="cantidad-input">
                      <input
                        type="number"
                        value={cantidad}
                        onChange={(e) => actualizarCantidadInsumo(codigo, e.target.value)}
                        min="0"
                        step="0.1"
                      />
                      <span>{insumo?.unidad_medida || 'unidad'}</span>
                      <button 
                        onClick={() => actualizarCantidadInsumo(codigo, 0)}
                        className="btn-remove"
                      >
                        ❌
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          <div className="colores-section">
            <h3>🎨 Colores (Opcional)</h3>
            <div className="colores-grid-small">
              {data.colores.map(color => (
                <div 
                  key={color.codigo} 
                  className={`color-option ${coloresSeleccionados.includes(color.codigo) ? 'selected' : ''}`}
                  onClick={() => toggleColor(color.codigo)}
                >
                  <div 
                    className="color-circle-small"
                    style={{ backgroundColor: getColorByName(color.nombre) }}
                  ></div>
                  <small>{color.codigo}</small>
                </div>
              ))}
            </div>
          </div>

          <div className="parametros-section">
            <h3>⚙️ Parámetros de Cálculo</h3>
            
            <div className="parametro-group">
              <label>Nivel de Calidad:</label>
              <select 
                value={nivelCalidad} 
                onChange={(e) => setNivelCalidad(parseInt(e.target.value))}
              >
                <option value={1}>1 - Premium (Factor 3.2)</option>
                <option value={2}>2 - Alta (Factor 3.0)</option>
                <option value={3}>3 - Estándar (Factor 2.8)</option>
                <option value={4}>4 - Básica (Factor 2.6)</option>
              </select>
            </div>

            <div className="parametro-group">
              <label>Cantidad a Producir:</label>
              <input 
                type="number" 
                value={cantidadProducir}
                onChange={(e) => setCantidadProducir(parseInt(e.target.value) || 1)}
                min="1"
              />
            </div>

            <div className="parametro-group">
              <label>Margen Adicional ($):</label>
              <input 
                type="number" 
                value={margenAdicional}
                onChange={(e) => setMargenAdicional(parseFloat(e.target.value) || 0)}
                min="0"
                step="100"
              />
            </div>
          </div>
        </div>

        <div className="calculator-result">
          <div className="result-card">
            <h3>💰 Resultado del Cálculo</h3>
            
            {resultado ? (
              <div className="result-display">
                <div className="result-price">
                  <span className="currency">$</span>
                  <span className="amount">{resultado.precio_final_redondeado.toLocaleString()}</span>
                </div>
                <p>Precio final sugerido</p>

                <div className="result-details">
                  <div className="detail-row">
                    <span>Costo materiales:</span>
                    <span>${resultado.costo_total_materiales.toLocaleString()}</span>
                  </div>
                  <div className="detail-row">
                    <span>Factor calidad:</span>
                    <span>x{resultado.factor_calidad}</span>
                  </div>
                  <div className="detail-row">
                    <span>Ganancia total:</span>
                    <span className="profit">${resultado.ganancia_total_lote.toLocaleString()}</span>
                  </div>
                  <div className="detail-row">
                    <span>Margen:</span>
                    <span className="profit">{resultado.margen_porcentual.toFixed(1)}%</span>
                  </div>
                </div>

                {resultado.insumos_utilizados.length > 0 && (
                  <div className="insumos-detalle">
                    <h4>📋 Detalle de Insumos</h4>
                    {resultado.insumos_utilizados.map(insumo => (
                      <div key={insumo.codigo} className="insumo-detalle">
                        <span>{insumo.descripcion}</span>
                        <span>${insumo.costo_total}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="empty-result">
                <p>Selecciona molde e insumos para calcular el costo</p>
              </div>
            )}

            <button
              className={`btn-calculate ${calculando ? 'calculating' : ''}`}
              onClick={calcularCosto}
              disabled={!moldeSeleccionado || calculando}
            >
              {calculando ? '🔄 Calculando...' : '🧮 Calcular Costo'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Modal Component para agregar/editar
function Modal({ type, item, onClose, onSuccess, showNotification }) {
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (item) {
      setFormData(item);
    } else {
      // Datos por defecto según el tipo
      if (type === 'add-insumo') {
        setFormData({
          codigo: '',
          descripcion: '',
          tipo: 'otros',
          costo_base: 0,
          cantidad_inventario: 0,
          unidad_medida: 'unidad',
          proveedor: '',
          activo: true
        });
      } else if (type === 'add-molde') {
        setFormData({
          codigo: '',
          descripcion: '',
          peso_cera_necesario: 0,
          cantidad_pabilo: 0,
          estado: 'disponible',
          ubicacion_fisica: '',
          dimensiones: '',
          precio_base_calculado: 0,
          activo: true
        });
      }
    }
  }, [type, item]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      let url, method, body;

      if (type === 'add-insumo') {
        url = `${API_BASE_URL}/insumos`;
        method = 'POST';
        body = formData;
      } else if (type === 'edit-insumo') {
        url = `${API_BASE_URL}/insumos/${item.codigo}`;
        method = 'PUT';
        body = formData;
      } else if (type === 'add-molde') {
        url = `${API_BASE_URL}/moldes`;
        method = 'POST';
        body = formData;
      } else if (type === 'edit-molde') {
        url = `${API_BASE_URL}/moldes/${item.codigo}`;
        method = 'PUT';
        body = formData;
      }

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
      });

      if (response.ok) {
        const result = await response.json();
        showNotification(result.message || '✅ Operación exitosa');
        onSuccess();
      } else {
        const error = await response.json();
        showNotification(`❌ Error: ${error.detail}`);
      }
    } catch (error) {
      showNotification('❌ Error en la operación');
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field, value) => {
    setFormData({
      ...formData,
      [field]: value
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>
            {type === 'add-insumo' && '➕ Agregar Insumo'}
            {type === 'edit-insumo' && '✏️ Editar Insumo'}
            {type === 'add-molde' && '➕ Agregar Molde'}
            {type === 'edit-molde' && '✏️ Editar Molde'}
          </h3>
          <button className="modal-close" onClick={onClose}>❌</button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          {(type === 'add-insumo' || type === 'edit-insumo') && (
            <>
              <div className="form-group">
                <label>Código:</label>
                <input
                  type="text"
                  value={formData.codigo || ''}
                  onChange={(e) => updateField('codigo', e.target.value)}
                  required
                  disabled={type === 'edit-insumo'}
                />
              </div>

              <div className="form-group">
                <label>Descripción:</label>
                <input
                  type="text"
                  value={formData.descripcion || ''}
                  onChange={(e) => updateField('descripcion', e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label>Tipo:</label>
                <select
                  value={formData.tipo || 'otros'}
                  onChange={(e) => updateField('tipo', e.target.value)}
                  required
                >
                  <option value="cera">Cera</option>
                  <option value="fragancia">Fragancia</option>
                  <option value="colorante">Colorante</option>
                  <option value="pabilo">Pabilo</option>
                  <option value="aditivo">Aditivo</option>
                  <option value="envase">Envase</option>
                  <option value="otros">Otros</option>
                </select>
              </div>

              <div className="form-group">
                <label>Costo Base:</label>
                <input
                  type="number"
                  value={formData.costo_base || ''}
                  onChange={(e) => updateField('costo_base', parseFloat(e.target.value))}
                  required
                  min="0"
                  step="0.01"
                />
              </div>

              <div className="form-group">
                <label>Cantidad en Inventario:</label>
                <input
                  type="number"
                  value={formData.cantidad_inventario || ''}
                  onChange={(e) => updateField('cantidad_inventario', parseInt(e.target.value))}
                  min="0"
                />
              </div>

              <div className="form-group">
                <label>Unidad de Medida:</label>
                <input
                  type="text"
                  value={formData.unidad_medida || ''}
                  onChange={(e) => updateField('unidad_medida', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Proveedor:</label>
                <input
                  type="text"
                  value={formData.proveedor || ''}
                  onChange={(e) => updateField('proveedor', e.target.value)}
                />
              </div>
            </>
          )}

          {(type === 'add-molde' || type === 'edit-molde') && (
            <>
              <div className="form-group">
                <label>Código:</label>
                <input
                  type="text"
                  value={formData.codigo || ''}
                  onChange={(e) => updateField('codigo', e.target.value)}
                  required
                  disabled={type === 'edit-molde'}
                />
              </div>

              <div className="form-group">
                <label>Descripción:</label>
                <input
                  type="text"
                  value={formData.descripcion || ''}
                  onChange={(e) => updateField('descripcion', e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label>Peso de Cera Necesario (g):</label>
                <input
                  type="number"
                  value={formData.peso_cera_necesario || ''}
                  onChange={(e) => updateField('peso_cera_necesario', parseFloat(e.target.value))}
                  required
                  min="0"
                  step="0.1"
                />
              </div>

              <div className="form-group">
                <label>Cantidad de Pabilo:</label>
                <input
                  type="number"
                  value={formData.cantidad_pabilo || ''}
                  onChange={(e) => updateField('cantidad_pabilo', parseInt(e.target.value))}
                  required
                  min="0"
                />
              </div>

              <div className="form-group">
                <label>Estado:</label>
                <select
                  value={formData.estado || 'disponible'}
                  onChange={(e) => updateField('estado', e.target.value)}
                >
                  <option value="disponible">Disponible</option>
                  <option value="en_uso">En Uso</option>
                  <option value="mantenimiento">Mantenimiento</option>
                </select>
              </div>

              <div className="form-group">
                <label>Ubicación Física:</label>
                <input
                  type="text"
                  value={formData.ubicacion_fisica || ''}
                  onChange={(e) => updateField('ubicacion_fisica', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Dimensiones:</label>
                <input
                  type="text"
                  value={formData.dimensiones || ''}
                  onChange={(e) => updateField('dimensiones', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Precio Base Calculado:</label>
                <input
                  type="number"
                  value={formData.precio_base_calculado || ''}
                  onChange={(e) => updateField('precio_base_calculado', parseFloat(e.target.value))}
                  min="0"
                  step="0.01"
                />
              </div>
            </>
          )}

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn-cancel">
              Cancelar
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Función auxiliar para colores
function getColorByName(nombre) {
  const colores = {
    'Ultramarine': '#120A8F',
    'Fluorescent blue': '#0080FF',
    'Blue': '#0000FF',
    'Cerulean blue': '#2A52BE'
  };
  return colores[nombre] || '#' + Math.floor(Math.random()*16777215).toString(16);
}

export default App;
