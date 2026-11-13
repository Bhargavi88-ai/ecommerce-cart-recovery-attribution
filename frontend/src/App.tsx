import React, { useState } from 'react';
import { Layout } from './components/Layout';
import { PageId } from './components/Sidebar';

import { OverviewDashboard } from './pages/OverviewDashboard';
import { CustomerManagement } from './pages/CustomerManagement';
import { ConsentManagement } from './pages/ConsentManagement';
import { CartManagement } from './pages/CartManagement';
import { AbandonedCartMonitoring } from './pages/AbandonedCartMonitoring';
import { CampaignManagement } from './pages/CampaignManagement';
import { MessageEventTracking } from './pages/MessageEventTracking';
import { OrderManagement } from './pages/OrderManagement';
import { ConversionAttribution } from './pages/ConversionAttribution';
import { AnomalyManagement } from './pages/AnomalyManagement';
import { DataValidation } from './pages/DataValidation';
import { DatasetExports } from './pages/DatasetExports';

export function App() {
  const [currentPage, setCurrentPage] = useState<PageId>('overview');
  const [refreshKey, setRefreshKey] = useState(0);

  const getPageTitle = (page: PageId) => {
    switch (page) {
      case 'overview':
        return 'Overview Dashboard';
      case 'customers':
        return 'Customer Directory & Preferences';
      case 'consents':
        return 'Communication Consent & Opt-Out Log';
      case 'carts':
        return 'Shopping Cart Lifecycle Management';
      case 'abandoned':
        return 'Abandoned Cart Recovery Pipeline';
      case 'campaigns':
        return 'Campaign Engine & Message Templates';
      case 'messages':
        return 'Message Dispatch & Telemetry Events';
      case 'orders':
        return 'Orders Placed & Conversion History';
      case 'attributions':
        return 'Campaign Attribution & Revenue Audit';
      case 'anomalies':
        return 'Anomaly & Exception Management';
      case 'validation':
        return 'Automated Data Quality Validation';
      case 'exports':
        return 'Dataset Generator & Reproducible Exports';
      default:
        return 'Dashboard';
    }
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'overview':
        return <OverviewDashboard key={refreshKey} />;
      case 'customers':
        return <CustomerManagement key={refreshKey} />;
      case 'consents':
        return <ConsentManagement key={refreshKey} />;
      case 'carts':
        return <CartManagement key={refreshKey} />;
      case 'abandoned':
        return <AbandonedCartMonitoring key={refreshKey} />;
      case 'campaigns':
        return <CampaignManagement key={refreshKey} />;
      case 'messages':
        return <MessageEventTracking key={refreshKey} />;
      case 'orders':
        return <OrderManagement key={refreshKey} />;
      case 'attributions':
        return <ConversionAttribution key={refreshKey} />;
      case 'anomalies':
        return <AnomalyManagement key={refreshKey} />;
      case 'validation':
        return <DataValidation key={refreshKey} />;
      case 'exports':
        return <DatasetExports key={refreshKey} />;
      default:
        return <OverviewDashboard key={refreshKey} />;
    }
  };

  return (
    <Layout
      currentPage={currentPage}
      onNavigate={setCurrentPage}
      pageTitle={getPageTitle(currentPage)}
      onRefresh={() => setRefreshKey((prev) => prev + 1)}
    >
      {renderPage()}
    </Layout>
  );
}

export default App;
