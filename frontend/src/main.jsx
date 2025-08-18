//react core
import React, { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

//router
import {
  createBrowserRouter,
  RouterProvider,
} from 'react-router-dom'

import './index.css'

//app pages (for your <RouterProvider>)
import AIAssistant from './AIAssistant.jsx'
import StoreDataExplorer from './StoreData.jsx'
import QueryData from './QueryData.jsx'
import Dashboard from './Dashboard.jsx'
import Reports from './Reports.jsx'

const router = createBrowserRouter([
  {
    path: "/assistant",
    element: <AIAssistant />
  }, {
    path: "/storedata",
    element: <StoreDataExplorer />
  }, {
    path: "/querydata",
    element: <QueryData />
  }, {
    path: "/dashboard",
    element: <Dashboard />
  }, {
    path: "/reports",
    element: <Reports />
  }
]);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);