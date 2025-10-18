const emojis = ['🌿', '🚲', '🌞', '🌍', '🚶', '🌱', '💚', '🛣️', '🏙️', '⚡', '🌳', '☀️', '🌺', '🦋'];

const form = document.getElementById('comunidadForm');
const muralesGrid = document.getElementById('murales-grid');
const totalVoices = document.getElementById('total-voices');
const filterTabs = document.querySelectorAll('.filter-tab');

let currentFilter = 'all';

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const nombre = document.getElementById('nombre').value.trim();
    const mensaje = document.getElementById('mensaje').value.trim();
    const tema = document.getElementById('tema').value;
    
    if (!nombre || !mensaje) return;
    
    const submitBtn = form.querySelector('.btn-submit');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Publicando...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch('/api/comunidad/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nombre, mensaje, tema })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            if (muralesGrid.querySelector('.empty-state')) {
                muralesGrid.innerHTML = '';
            }
            
            agregarMensajeAlMural(data);
            
            form.reset();
            
            const count = parseInt(totalVoices.textContent);
            totalVoices.textContent = count + 1;
            
            mostrarNotificacion('¡Tu voz ha sido compartida! 🎉', 'success');
        } else {
            mostrarNotificacion('Error al publicar. Intenta de nuevo.', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error de conexión. Verifica tu internet.', 'error');
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
});

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function agregarMensajeAlMural(data) {
    const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)];
    
    const card = document.createElement('div');
    card.className = 'mural-card';
    card.setAttribute('data-id', data.id);
    card.setAttribute('data-tema', data.tema || 'general');
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    
    const cardHeader = document.createElement('div');
    cardHeader.className = 'card-header';
    
    const cardIcon = document.createElement('div');
    cardIcon.className = 'card-icon';
    cardIcon.textContent = randomEmoji;
    
    const cardInfo = document.createElement('div');
    cardInfo.className = 'card-info';
    
    const cardName = document.createElement('h4');
    cardName.textContent = data.nombre;
    
    const cardDate = document.createElement('span');
    cardDate.className = 'card-date';
    cardDate.textContent = data.fecha;
    
    cardInfo.appendChild(cardName);
    cardInfo.appendChild(cardDate);
    cardHeader.appendChild(cardIcon);
    cardHeader.appendChild(cardInfo);
    
    if (data.tema && data.tema !== 'general') {
        const badge = document.createElement('span');
        badge.className = `card-badge badge-${data.tema}`;
        badge.textContent = data.tema.charAt(0).toUpperCase() + data.tema.slice(1);
        cardHeader.appendChild(badge);
    }
    
    const cardBody = document.createElement('div');
    cardBody.className = 'card-body';
    const cardText = document.createElement('p');
    cardText.textContent = data.mensaje;
    cardBody.appendChild(cardText);
    
    const cardFooter = document.createElement('div');
    cardFooter.className = 'card-footer';
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'btn-delete';
    deleteBtn.onclick = () => eliminarMensaje(data.id);
    deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i>';
    cardFooter.appendChild(deleteBtn);
    
    card.appendChild(cardHeader);
    card.appendChild(cardBody);
    card.appendChild(cardFooter);
    
    muralesGrid.insertBefore(card, muralesGrid.firstChild);
    
    setTimeout(() => {
        card.style.transition = 'all 0.5s ease';
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
    }, 100);
    
    if (currentFilter !== 'all' && currentFilter !== data.tema) {
        aplicarFiltro(currentFilter);
    }
}

async function eliminarMensaje(id) {
    if (!confirm('¿Estás seguro de eliminar este mensaje?')) {
        return;
    }
    
    const card = document.querySelector(`.mural-card[data-id="${id}"]`);
    
    if (!card) return;
    
    card.style.transition = 'all 0.4s ease';
    card.style.opacity = '0';
    card.style.transform = 'scale(0.8)';
    
    try {
        const response = await fetch(`/api/comunidad/delete/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            setTimeout(() => {
                card.remove();
                
                const count = parseInt(totalVoices.textContent);
                totalVoices.textContent = Math.max(0, count - 1);
                
                if (muralesGrid.children.length === 0) {
                    muralesGrid.innerHTML = `
                        <div class="empty-state">
                            <i class="fas fa-comments"></i>
                            <p>Sé la primera voz en compartir tu visión</p>
                            <p class="empty-subtitle">Tu mensaje puede inspirar cambios en Urabá</p>
                        </div>
                    `;
                }
            }, 400);
            
            mostrarNotificacion('Mensaje eliminado correctamente', 'success');
        } else {
            card.style.opacity = '1';
            card.style.transform = 'scale(1)';
            mostrarNotificacion('Error al eliminar el mensaje', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        card.style.opacity = '1';
        card.style.transform = 'scale(1)';
        mostrarNotificacion('Error de conexión', 'error');
    }
}

filterTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        filterTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        const filter = tab.getAttribute('data-filter');
        currentFilter = filter;
        aplicarFiltro(filter);
    });
});

function aplicarFiltro(filter) {
    const cards = document.querySelectorAll('.mural-card');
    
    cards.forEach(card => {
        const tema = card.getAttribute('data-tema');
        
        if (filter === 'all' || tema === filter) {
            card.style.display = '';
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'scale(1)';
            }, 50);
        } else {
            card.style.opacity = '0';
            card.style.transform = 'scale(0.95)';
            setTimeout(() => {
                card.style.display = 'none';
            }, 300);
        }
    });
}

function mostrarNotificacion(mensaje, tipo) {
    const notif = document.createElement('div');
    notif.className = `notificacion notificacion-${tipo}`;
    notif.innerHTML = `
        <i class="fas fa-${tipo === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${mensaje}</span>
    `;
    
    document.body.appendChild(notif);
    
    setTimeout(() => {
        notif.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notif.classList.remove('show');
        setTimeout(() => {
            notif.remove();
        }, 300);
    }, 3000);
}
