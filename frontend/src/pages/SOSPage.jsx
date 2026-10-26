
import SOSForm from '../components/sos/SOSForm.jsx'

export default function SOSPage() {
  return (
    <div className="h-full overflow-y-auto p-6 flex justify-center">
      <div className="w-full max-w-xl">
        <h1 className="text-xl font-semibold mb-1">Citizen Emergency Report</h1>
        <p className="text-slate-400 text-sm mb-4">
          Submit an SOS. Your description will be triaged by the lexicon classifier
          and an incident will be created for responder review.
        </p>
        <SOSForm />
      </div>
    </div>
  )
}
