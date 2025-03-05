Option Explicit
Option Base 1

Sub UpdateValidationLists()

    Dim valueCellInDataTable As Range
    Dim strFeatureID As String

    Dim strAddressOfRangeWithPossibleValues As String

    Sheets("input").Unprotect

    Call LoadData

    For Each valueCellInDataTable In [InputForm].Columns(5).Cells
        strFeatureID = valueCellInDataTable.Offset(0, -4).Value

        'I have to work with address of range of cells, not with Array of values.
        'If Array of values is longer than 254 characters, it will give error on re-opening the file
        ' because data validation field cannot be longer than 254 characters
        strAddressOfRangeWithPossibleValues = GetAddressOfRangeWithPossibleValuesForFeatureID(strFeatureID)

        If strAddressOfRangeWithPossibleValues <> ":" Then
            Call AddValidationToOneCell(valueCellInDataTable, strAddressOfRangeWithPossibleValues)
        End If

    Next valueCellInDataTable

    Sheets("input").Protect DrawingObjects:=True, Contents:=True, Scenarios:=True _
        , AllowFormattingColumns:=True, AllowFiltering:=True

    Application.StatusBar = ""

End Sub


Sub LoadData()

    ThisWorkbook.RefreshAll

    With Application
        .StatusBar = "Ожидаю загрузки данных из внешнего источника..."
        .CalculateUntilAsyncQueriesDone
        .StatusBar = "Загрузка данных из внешнего источника завершена."
    End With

End Sub


Function GetAddressOfRangeWithPossibleValuesForFeatureID(strRelevantFeatureID As String)

    Dim strAddressOfFirstRelevantValueCell
    Dim strAddressOfLastRelevantValueCell

    Dim rngFeatureCell As Range
    Dim rngValueCell As Range

    Dim strAddressOfRange As String

    For Each rngFeatureCell In [features_listed_values].Columns(2).Cells

        Set rngValueCell = rngFeatureCell.Offset(0, 2)

        If rngFeatureCell.Value = strRelevantFeatureID Then
            If strAddressOfFirstRelevantValueCell = "" Then strAddressOfFirstRelevantValueCell = rngValueCell.Address

            If rngFeatureCell.Offset(1, 0).Value <> strRelevantFeatureID Then
                strAddressOfLastRelevantValueCell = rngValueCell.Address
                Exit For
            End If

        End If

    Next rngFeatureCell

    strAddressOfRange = strAddressOfFirstRelevantValueCell & _
        ":" & strAddressOfLastRelevantValueCell

    GetAddressOfRangeWithPossibleValuesForFeatureID = strAddressOfRange

End Function


Sub AddValidationToOneCell(cell As Range, strAddressOfRangeWithPossibleValues As String)

    Dim strFormula As String

    strFormula = "=INDIRECT(""features_listed_values!#RANGE#"")"
    strFormula = Replace(strFormula, "#RANGE#", strAddressOfRangeWithPossibleValues)

    With cell.Validation
        .Delete
        .Add Type:=xlValidateList, AlertStyle:=xlValidAlertStop, Operator:= _
        xlBetween, Formula1:=strFormula
        .IgnoreBlank = True
        .InCellDropdown = True
        .InputTitle = ""
        .ErrorTitle = ""
        .InputMessage = ""
        .ErrorMessage = ""
        .ShowInput = True
        .ShowError = True
    End With

End Sub
