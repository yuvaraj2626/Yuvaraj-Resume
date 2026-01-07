import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import apiService from '../services/apiService';
import './Common.css';

function TicketsPage() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTickets();
  }, []);

  const fetchTickets = async () => {
    try {
      const response = await apiService.getTickets();
      setTickets(response.data.results || response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching tickets:', error);
      toast.error('Failed to load tickets');
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (ticketId, newStatus) => {
    try {
      await apiService.updateTicketStatus(ticketId, newStatus);
      toast.success('Ticket status updated');
      fetchTickets();
    } catch (error) {
      toast.error('Failed to update ticket');
    }
  };

  if (loading) {
    return <div className="loading-container"><div className="loading-spinner"></div></div>;
  }

  return (
    <div className="page-container">
      <h1>Tickets Management</h1>
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Ticket ID</th>
              <th>Device</th>
              <th>Issue Type</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {tickets.map((ticket) => (
              <tr key={ticket.id}>
                <td><strong>{ticket.ticket_id}</strong></td>
                <td>{ticket.device_name}</td>
                <td>{ticket.issue_type}</td>
                <td>
                  <span className={`severity-badge severity-${ticket.severity}`}>
                    {ticket.severity}
                  </span>
                </td>
                <td>
                  <span className={`status-badge status-${ticket.status}`}>
                    {ticket.status}
                  </span>
                </td>
                <td>{new Date(ticket.created_at).toLocaleString()}</td>
                <td>
                  {ticket.status === 'open' && (
                    <button 
                      onClick={() => handleStatusUpdate(ticket.id, 'in_progress')}
                      className="btn-sm btn-primary"
                    >
                      Start
                    </button>
                  )}
                  {ticket.status === 'in_progress' && (
                    <button 
                      onClick={() => handleStatusUpdate(ticket.id, 'resolved')}
                      className="btn-sm btn-success"
                    >
                      Resolve
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TicketsPage;
