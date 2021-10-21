# Copyright (c) 2021 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from cura.CuraApplication import CuraApplication
from cura.UltimakerCloud.UltimakerCloudScope import UltimakerCloudScope  # To make requests to the Ultimaker API with correct authorization.
from PyQt5.QtCore import pyqtProperty, pyqtSignal, pyqtSlot, Qt
from typing import List, Optional, TYPE_CHECKING
from UM.Qt.ListModel import ListModel
from UM.TaskManagement.HttpRequestManager import HttpRequestManager  # To request the package list from the API.
from UM.TaskManagement.HttpRequestScope import JsonDecoratorScope  # To request JSON responses from the API.

from . import Marketplace   # To get the list of packages. Imported this way to prevent circular imports.
from .PackageModel import PackageModel  # This list is a list of PackageModels.

if TYPE_CHECKING:
    from PyQt5.QtCore import QObject
    from PyQt5.QtNetwork import QNetworkReply

class PackageList(ListModel):
    """
    Represents a list of packages to be displayed in the interface.

    The list can be filtered (e.g. on package type, materials vs. plug-ins) and
    paginated.
    """

    PackageRole = Qt.UserRole + 1

    ITEMS_PER_PAGE = 20  # Pagination of number of elements to download at once.

    def __init__(self, parent: "QObject" = None):
        super().__init__(parent)

        self._packages: List[PackageModel] = []
        self._is_loading = True
        self._scope = JsonDecoratorScope(UltimakerCloudScope(CuraApplication.getInstance()))

        self.requestFirst()

    def requestFirst(self) -> None:
        """
        Make a request for the first paginated page of packages.

        When the request is done, the list will get updated with the new package models.
        """
        self.setIsLoading(True)

        http = HttpRequestManager.getInstance()
        http.get(
            Marketplace.PACKAGES_URL,
            scope = self._scope,
            callback = self._parseResponse,
            error_callback = self._onError
        )

    isLoadingChanged = pyqtSignal()

    @pyqtSlot(bool)
    def setIsLoading(self, is_loading: bool) -> None:
        if(is_loading != self._is_loading):
            self._is_loading = is_loading
            self.isLoadingChanged.emit()

    @pyqtProperty(bool, notify = isLoadingChanged, fset = setIsLoading)
    def isLoading(self) -> bool:
        """
        Gives whether the list is currently loading the first page or loading more pages.
        :return: ``True`` if the list is downloading, or ``False`` if not downloading.
        """
        return self._is_loading

    def _parseResponse(self, reply: "QNetworkReply") -> None:
        """
        Parse the response from the package list API request.

        This converts that response into PackageModels, and triggers the ListModel to update.
        :param reply: A reply containing information about a number of packages.
        """
        response_data = HttpRequestManager.readJSON(reply)
        if "data" not in response_data:
            return  # TODO: Handle invalid response.

        for package_data in response_data["data"]:
            package = PackageModel(package_data, parent = self)
            self._packages.append(package)
        self._update()

    def _onError(self, reply: "QNetworkReply", error: Optional["QNetworkReply.NetworkError"]) -> None:
        """
        Handles networking and server errors when requesting the list of packages.
        :param reply: The reply with packages. This will most likely be incomplete and should be ignored.
        :param error: The error status of the request.
        """
        pass  # TODO: Handle errors.

    def _update(self) -> None:
        # TODO: Get list of packages from Marketplace class.
        pass
