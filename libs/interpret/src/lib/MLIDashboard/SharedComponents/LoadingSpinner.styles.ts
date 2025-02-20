// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
  IStyle,
  mergeStyleSets,
  IProcessedStyleSet
} from "office-ui-fabric-react";

export interface ILoadingSpinnerStyles {
  explanationSpinner: IStyle;
}

export const loadingSpinnerStyles: IProcessedStyleSet<ILoadingSpinnerStyles> =
  mergeStyleSets<ILoadingSpinnerStyles>({
    explanationSpinner: {
      fontFamily: `"Segoe UI", "Segoe UI Web (West European)", "Segoe UI",
      -apple-system, BlinkMacSystemFont, Roboto, "Helvetica Neue", sans-serif`,
      margin: "auto",
      padding: "40px"
    }
  });
