import React, { useState, useEffect } from 'react';
import { SendHorizontal, Plus, FileText, CheckCircle2, XCircle, ChevronRight } from 'lucide-react';
import { api } from '../services/api';
import { Campaign } from '../types';
import { StatusBadge } from '../components/StatusBadge';

export const CampaignManagement: React.FC = () => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Form state
  const [name, setName] = useState('');
  const [channel, setChannel] = useState('EMAIL');
  const [triggerDelay, setTriggerDelay] = useState(60);
  const [discountPercent, setDiscountPercent] = useState(10);
  const [submitting, setSubmitting] = useState(false);

  const fetchCampaigns = async () => {
    try {
      setLoading(true);
      const res = await api.getCampaigns();
      setCampaigns(res.items);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const inspectCampaign = async (cId: string) => {
    try {
      const detailed = await api.getCampaignById(cId);
      setSelectedCampaign(detailed);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      await api.createCampaign({
        name,
        channel,
        trigger_delay_minutes: triggerDelay,
        discount_percent: discountPercent,
        is_active: true,
      });
      setShowCreateModal(false);
      setName('');
      fetchCampaigns();
    } catch (err: any) {
      alert(`Error creating campaign: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  useEffect(() => {
    fetchCampaigns();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header and Action */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-white">Campaign Variants & Message Templates</h3>
          <p className="text-xs text-slate-400">
            Multi-channel automated recovery campaigns triggered by inactivity thresholds
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-sm shadow-indigo-600/30 transition-all"
        >
          <Plus className="w-4 h-4" /> Create Campaign
        </button>
      </div>

      {/* Campaigns Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full py-12 text-center text-slate-400">Loading campaigns...</div>
        ) : campaigns.length === 0 ? (
          <div className="col-span-full py-12 text-center text-slate-400">No campaigns defined yet.</div>
        ) : (
          campaigns.map((camp) => (
            <div
              key={camp.campaign_id}
              className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-all space-y-4 flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-indigo-400">
                    {camp.campaign_id}
                  </span>
                  <StatusBadge status={camp.is_active ? 'ACTIVE' : 'INACTIVE'} />
                </div>
                <h4 className="font-bold text-white text-base leading-snug">{camp.name}</h4>
              </div>

              <div className="space-y-2 text-xs text-slate-300 py-3 border-y border-slate-800/80">
                <div className="flex justify-between">
                  <span className="text-slate-400">Channel</span>
                  <span className="font-semibold text-white">{camp.channel}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Inactivity Trigger Delay</span>
                  <span>{camp.trigger_delay_minutes} minutes</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Discount Offer</span>
                  <span className="font-semibold text-emerald-400">{camp.discount_percent}% OFF</span>
                </div>
              </div>

              <button
                onClick={() => inspectCampaign(camp.campaign_id)}
                className="w-full flex items-center justify-center gap-1.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-indigo-300 transition-colors"
              >
                <FileText className="w-3.5 h-3.5" /> View Templates & Copy
              </button>
            </div>
          ))
        )}
      </div>

      {/* Templates Modal */}
      {selectedCampaign && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <span className="font-mono text-xs text-indigo-400">{selectedCampaign.campaign_id}</span>
                <h3 className="font-bold text-white text-lg">{selectedCampaign.name}</h3>
              </div>
              <button
                onClick={() => setSelectedCampaign(null)}
                className="text-slate-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Message Variant Templates
              </h4>
              {selectedCampaign.templates && selectedCampaign.templates.length > 0 ? (
                selectedCampaign.templates.map((tmpl) => (
                  <div key={tmpl.template_id} className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-mono text-indigo-300 font-semibold">{tmpl.template_id}</span>
                      <span className="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-bold">
                        Variant {tmpl.variant}
                      </span>
                    </div>
                    {tmpl.subject && (
                      <div>
                        <span className="text-[11px] text-slate-400 block">Subject Line:</span>
                        <p className="text-xs font-semibold text-slate-200 font-mono bg-slate-900 p-2 rounded border border-slate-800">
                          {tmpl.subject}
                        </p>
                      </div>
                    )}
                    <div>
                      <span className="text-[11px] text-slate-400 block">Body Copy Template:</span>
                      <p className="text-xs text-slate-300 font-mono bg-slate-900 p-2.5 rounded border border-slate-800 whitespace-pre-wrap leading-relaxed">
                        {tmpl.body_template}
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-400 italic">No templates attached to this campaign.</p>
              )}
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedCampaign(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Campaign Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <form
            onSubmit={handleCreate}
            className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4"
          >
            <h3 className="font-bold text-white text-base border-b border-slate-800 pb-3">
              Create Recovery Campaign
            </h3>

            <div className="space-y-3 text-sm">
              <div>
                <label className="text-xs text-slate-400 block mb-1">Campaign Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. VIP Abandoned Cart Recovery Email"
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 block mb-1">Channel</label>
                <select
                  value={channel}
                  onChange={(e) => setChannel(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="EMAIL">Email</option>
                  <option value="SMS">SMS</option>
                </select>
              </div>

              <div>
                <label className="text-xs text-slate-400 block mb-1">Trigger Inactivity Delay (Minutes)</label>
                <input
                  type="number"
                  min="1"
                  value={triggerDelay}
                  onChange={(e) => setTriggerDelay(Number(e.target.value))}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 block mb-1">Discount Percent (%)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={discountPercent}
                  onChange={(e) => setDiscountPercent(Number(e.target.value))}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="pt-3 flex justify-end gap-3 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold disabled:opacity-50"
              >
                {submitting ? 'Creating...' : 'Create Campaign'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

