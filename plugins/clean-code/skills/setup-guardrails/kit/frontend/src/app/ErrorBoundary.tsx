// The single place for UNEXPECTED errors (bugs). Expected failures are Result values.
import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  readonly children: ReactNode;
  readonly onError: (error: unknown, info: ErrorInfo) => void;
}

interface State {
  readonly crashed: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  override state: State = { crashed: false };

  static getDerivedStateFromError(): State {
    return { crashed: true };
  }

  override componentDidCatch(error: unknown, info: ErrorInfo): void {
    this.props.onError(error, info);
  }

  override render(): ReactNode {
    return this.state.crashed ? <p role="alert">Something went wrong.</p> : this.props.children;
  }
}
