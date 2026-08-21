import { AppShell } from './components/layout/AppShell';
import { AppRoutes } from './routes';

export function App() {
  return (
    <AppShell>
      <AppRoutes />
    </AppShell>
  );
}
