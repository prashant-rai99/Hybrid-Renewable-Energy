'use client';

import { useEffect, useState } from 'react';
import { getEnergyData } from '@/lib/utils';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Download, FileText, Calendar, Share2 } from 'lucide-react';

export default function ReportsPage() {

  const [energyData, setEnergyData] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      const data = await getEnergyData();
      setEnergyData(data);
    };

    fetchData();
  }, []);

  if (!energyData) {
    return <div className="text-center mt-20 text-xl">Loading Reports...</div>;
  }

  // ✅ dynamic reports (replace mockReports)
  const reports = [
    {
      id: 1,
      title: 'Energy Summary',
      period: 'Today',
      generated: 'Now',
      carbon: `${(energyData.solar_prediction * 0.02).toFixed(2)} kg CO₂ saved`
    },
    {
      id: 2,
      title: 'Solar Performance',
      period: 'Today',
      generated: 'Auto',
      carbon: `${(energyData.solar_prediction * 0.01).toFixed(2)} kg CO₂`
    },
    {
      id: 3,
      title: 'Wind Report',
      period: 'Today',
      generated: 'Auto',
      carbon: `${(energyData.wind_prediction * 0.01).toFixed(2)} kg CO₂`
    }
  ];

  return (
    <div className="space-y-8">

      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold mb-2">Reports</h2>
        <p className="text-muted-foreground">Energy insights & downloads</p>
      </div>

      {/* Generate */}
      <Card>
        <CardHeader>
          <CardTitle>Generate Report</CardTitle>
        </CardHeader>
        <CardContent className="flex gap-3">
          <Button>
            <FileText className="w-4 h-4 mr-2" />
            Generate
          </Button>
          <Button variant="outline">
            <Share2 className="w-4 h-4 mr-2" />
            Share
          </Button>
        </CardContent>
      </Card>

      {/* Reports List */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Reports</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {reports.map((r) => (
            <div key={r.id} className="flex justify-between p-3 border rounded">
              <div>
                <p className="font-semibold">{r.title}</p>
                <p className="text-xs text-gray-400">{r.period} • {r.generated}</p>
                <p className="text-xs text-green-500">{r.carbon}</p>
              </div>

              <div className="flex gap-2">
                <Button size="sm" variant="outline">
                  <Download />
                </Button>
                <Button size="sm" variant="outline">
                  <Share2 />
                </Button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Live Summary</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-4">

          <div>
            <p className="text-sm">Solar</p>
            <p className="text-xl font-bold text-yellow-500">
              {energyData.solar_prediction.toFixed(2)} kW
            </p>
          </div>

          <div>
            <p className="text-sm">Wind</p>
            <p className="text-xl font-bold text-blue-500">
              {energyData.wind_prediction.toFixed(2)} kW
            </p>
          </div>

          <div>
            <p className="text-sm">Demand</p>
            <p className="text-xl font-bold text-red-500">
              {energyData.decision.energy_used} kW
            </p>
          </div>

          <div>
            <p className="text-sm">Battery</p>
            <p className="text-xl font-bold text-green-500">
              {energyData.decision.battery_action}
            </p>
          </div>

        </CardContent>
      </Card>

    </div>
  );
}