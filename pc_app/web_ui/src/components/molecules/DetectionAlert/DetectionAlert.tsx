interface DetectionAlertProps {
  personDetected?: boolean;
}

export function DetectionAlert({ personDetected = false }: DetectionAlertProps) {
  if (!personDetected) {
    return <div className="alert neutral">No person detected</div>;
  }

  return <div className="alert danger">Person detected</div>;
}
