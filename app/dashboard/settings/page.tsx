'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useState } from 'react';
import { Save, AlertCircle } from 'lucide-react';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('system');
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="space-y-8">
      {/* Page Title */}
      <div>
        <h2 className="text-3xl font-bold text-foreground mb-2">Settings</h2>
        <p className="text-muted-foreground">Configure your energy system and preferences</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border pb-0 overflow-x-auto">
        {[
          { id: 'system', label: 'System Configuration' },
          { id: 'alerts', label: 'Alerts & Notifications' },
          { id: 'account', label: 'Account Settings' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
              activeTab === tab.id
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* System Configuration */}
      {activeTab === 'system' && (
        <div className="space-y-6 animate-in fade-in">
          {/* Energy Source Settings */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-foreground">Energy Source Configuration</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Solar */}
                <div>
                  <h4 className="font-semibold text-foreground mb-4">Solar Panels</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-foreground mb-2 block">Installed Capacity (kW)</label>
                      <Input type="number" defaultValue={3000} className="bg-input border-border text-foreground" />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-foreground mb-2 block">Panel Type</label>
                      <select className="w-full bg-input border border-border rounded-lg px-3 py-2 text-foreground text-sm">
                        <option>Monocrystalline</option>
                        <option>Polycrystalline</option>
                        <option>Thin-film</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-foreground mb-2 block">Tilt Angle (degrees)</label>
                      <Input type="number" defaultValue={25} className="bg-input border-border text-foreground" />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-foreground mb-2 block">Azimuth (degrees)</label>
                      <Input type="number" defaultValue={180} className="bg-input border-border text-foreground" />
                    </div>
                  </div>
                </div>

                <div className="border-t border-border pt-6">
                  {/* Wind */}
                  <h4 className="font-semibold text-foreground mb-4">Wind Turbines</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-foreground mb-2 block">Installed Capacity (kW)</label>
                      <Input type="number" defaultValue={2500} className="bg-input border-border text-foreground" />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-foreground mb-2 block">Hub Height (m)</label>
                      <Input type="number" defaultValue={50} className="bg-input border-border text-foreground" />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-foreground mb-2 block">Cut-in Speed (km/h)</label>
                      <Input type="number" defaultValue={12} className="bg-input border-border text-foreground" />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-foreground mb-2 block">Rated Speed (km/h)</label>
                      <Input type="number" defaultValue={35} className="bg-input border-border text-foreground" />
                    </div>
                  </div>
                </div>

                <div className="border-t border-border pt-6">
                  {/* Battery */}
                  <h4 className="font-semibold text-foreground mb-4">Battery Storage</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-foreground mb-2 block">Total Capacity (kWh)</label>
                      <Input type="number" defaultValue={5000} className="bg-input border-border text-foreground" />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-foreground mb-2 block">Battery Type</label>
                      <select className="w-full bg-input border border-border rounded-lg px-3 py-2 text-foreground text-sm">
                        <option>Lithium-ion</option>
                        <option>Lead-acid</option>
                        <option>Flow</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-foreground mb-2 block">Min Charge Level (%)</label>
                      <Input type="number" defaultValue={20} className="bg-input border-border text-foreground" />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-foreground mb-2 block">Max Charge Level (%)</label>
                      <Input type="number" defaultValue={80} className="bg-input border-border text-foreground" />
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Grid Settings */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-foreground">Grid Connection Settings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-foreground mb-2 block">Import Rate (£/kWh)</label>
                    <Input type="number" defaultValue={0.28} step={0.01} className="bg-input border-border text-foreground" />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-foreground mb-2 block">Export Rate (£/kWh)</label>
                    <Input type="number" defaultValue={0.12} step={0.01} className="bg-input border-border text-foreground" />
                  </div>
                </div>
                <div className="flex items-center gap-3 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                  <AlertCircle className="w-5 h-5 text-blue-500 flex-shrink-0" />
                  <p className="text-sm text-blue-500">Grid connection is active and functioning normally</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Button onClick={handleSave} className="bg-primary text-primary-foreground hover:opacity-90 w-full md:w-auto">
            <Save className="w-4 h-4 mr-2" />
            Save Configuration
          </Button>
        </div>
      )}

      {/* Alerts & Notifications */}
      {activeTab === 'alerts' && (
        <div className="space-y-6 animate-in fade-in">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-foreground">Alert Thresholds</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {[
                  { label: 'Low Battery Alert (%)', default: 20 },
                  { label: 'High Battery Alert (%)', default: 95 },
                  { label: 'Grid Import Threshold (kW)', default: 500 },
                  { label: 'System Efficiency Alert (%)', default: 85 },
                ].map((alert, i) => (
                  <div key={i}>
                    <label className="text-sm font-medium text-foreground mb-2 block">{alert.label}</label>
                    <Input type="number" defaultValue={alert.default} className="bg-input border-border text-foreground" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-foreground">Notification Preferences</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  'Email alerts for critical issues',
                  'Daily summary report',
                  'Weekly performance analysis',
                  'Monthly cost summary',
                ].map((pref, i) => (
                  <label key={i} className="flex items-center gap-3 p-3 bg-muted/20 border border-border/50 rounded-lg hover:border-border transition-colors cursor-pointer">
                    <input type="checkbox" defaultChecked className="w-4 h-4 accent-primary" />
                    <span className="text-sm text-foreground">{pref}</span>
                  </label>
                ))}
              </div>
            </CardContent>
          </Card>

          <Button onClick={handleSave} className="bg-primary text-primary-foreground hover:opacity-90 w-full md:w-auto">
            <Save className="w-4 h-4 mr-2" />
            Save Preferences
          </Button>
        </div>
      )}

      {/* Account Settings */}
      {activeTab === 'account' && (
        <div className="space-y-6 animate-in fade-in">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-foreground">Profile Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-foreground mb-2 block">Full Name</label>
                    <Input defaultValue="Campus Manager" className="bg-input border-border text-foreground" />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-foreground mb-2 block">Email Address</label>
                    <Input type="email" defaultValue="admin@energyos.com" className="bg-input border-border text-foreground" />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-foreground mb-2 block">Organization</label>
                    <Input defaultValue="University Campus" className="bg-input border-border text-foreground" />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-foreground mb-2 block">Role</label>
                    <Input defaultValue="Energy Manager" className="bg-input border-border text-foreground" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-foreground">Security</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Button variant="outline" className="border-border text-foreground hover:bg-muted w-full md:w-auto">
                  Change Password
                </Button>
                <Button variant="outline" className="border-border text-foreground hover:bg-muted w-full md:w-auto">
                  Two-Factor Authentication
                </Button>
              </div>
            </CardContent>
          </Card>

          <Button onClick={handleSave} className="bg-primary text-primary-foreground hover:opacity-90 w-full md:w-auto">
            <Save className="w-4 h-4 mr-2" />
            Save Changes
          </Button>
        </div>
      )}

      {/* Success Message */}
      {saved && (
        <div className="fixed bottom-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg animate-in fade-in slide-in-from-bottom-4">
          Settings saved successfully!
        </div>
      )}
    </div>
  );
}
