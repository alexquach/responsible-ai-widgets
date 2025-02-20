// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
  IStyle,
  mergeStyleSets,
  IProcessedStyleSet
} from "office-ui-fabric-react";

export interface IScatterStyles {
  explanationChart: IStyle;
  topControls: IStyle;
  selector: IStyle;
  selectorLabel: IStyle;
  labelText: IStyle;
  selectorComboBox: IStyle;
  calloutInfo: IStyle;
  calloutButton: IStyle;
}

export const scatterStyles: IProcessedStyleSet<IScatterStyles> =
  mergeStyleSets<IScatterStyles>({
    calloutButton: {
      maxWidth: "100px"
    },
    calloutInfo: {
      display: "flex",
      flexDirection: "column",
      fontFamily: `"Segoe UI", "Segoe UI Web (West European)", "Segoe UI",
      -apple-system, BlinkMacSystemFont, Roboto, "Helvetica Neue", sans-serif`,
      maxWidth: "300px",
      padding: "30px"
    },
    explanationChart: {
      display: "flex",
      flex: "1",
      flexDirection: "column",
      height: "100%",
      width: "100%"
    },
    labelText: {
      fontFamily: ` "Segoe UI", "Segoe UI Web (West European)", "Segoe UI",
      -apple-system, BlinkMacSystemFont, Roboto, "Helvetica Neue",
      sans-serif`,
      fontSize: "14px",
      lineHeight: "14px",
      marginRight: "-16px",
      maxWidth: "84px"
    },
    selector: {
      display: "flex"
    },
    selectorComboBox: {
      maxWidth: "208px"
    },
    selectorLabel: {
      display: "flex",
      flexDirection: "row"
    },
    topControls: {
      display: "flex",
      justifyContent: "space-between",
      padding: "3px 15px"
    }
  });
