##########################################################################
#  
#  Copyright (c) 2011, John Haddon. All rights reserved.
#  Copyright (c) 2011-2012, Image Engine Design Inc. All rights reserved.
#  
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#  
#      * Redistributions of source code must retain the above
#        copyright notice, this list of conditions and the following
#        disclaimer.
#  
#      * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided with
#        the distribution.
#  
#      * Neither the name of John Haddon nor the names of
#        any other contributors to this software may be used to endorse or
#        promote products derived from this software without specific prior
#        written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#  
##########################################################################

import IECore

import Gaffer
import GafferUI

QtCore = GafferUI._qtImport( "QtCore" )
QtGui = GafferUI._qtImport( "QtGui" )

class TabbedContainer( GafferUI.ContainerWidget ) :

	def __init__( self, cornerWidget=None, **kw ) :
	
		GafferUI.ContainerWidget.__init__( self, QtGui.QTabWidget(), **kw )
		
		self._qtWidget().setUsesScrollButtons( False )
		self._qtWidget().setElideMode( QtCore.Qt.ElideNone )
		
		self.__widgets = []
		
		self.__cornerWidget = None
		self.setCornerWidget( cornerWidget )
		
		self.__currentChangedSignal = GafferUI.WidgetEventSignal()
		self._qtWidget().currentChanged.connect( Gaffer.WeakMethod( self.__currentChanged ) )
		
	def append( self, child, label="" ) :
	
		oldParent = child.parent()
		if oldParent :
			oldParent.removeChild( child )
	
		self.__widgets.append( child )
		self._qtWidget().addTab( child._qtWidget(), label )
		child._applyVisibility()
				
	def remove( self,  child ) :
	
		self.removeChild( child )
		
	def setLabel( self, child, labelText ) :
	
		self._qtWidget().setTabText( self.__widgets.index( child ), labelText )
			
	def getLabel( self, child ) :
		
		return str( self._qtWidget().tabText( self.__widgets.index( child ) ) )
	
	def setCurrent( self, child ) :
	
		self._qtWidget().setCurrentIndex( self.__widgets.index( child ) )

	def getCurrent( self ) :
	
		if not self.__widgets :
			return None
			
		return self.__widgets[ self._qtWidget().currentIndex() ]
		
	def __getitem__( self, index ) :
	
		return self.__widgets[index]
	
	def __delitem__( self, index ) :
	
		if isinstance( index, slice ) :
			indices = range( *(index.indices( len( self ) ) ) )
			for i in indices :
				self._qtWidget().removeTab( self._qtWidget().indexOf( self[i]._qtWidget() ) )
				self[i]._qtWidget().setParent( None )
				self[i]._applyVisibility()
			del self.__widgets[index]
		else :
			self.removeChild( self.__widgets[index] )
	
	def __len__( self ) :
	
		return len( self.__widgets )
		
	def index( self, child ) :
	
		return self.__widgets.index( child )
	
	def addChild( self, child ) :
	
		self.append( child )
	
	def removeChild( self, child ) :
	
		assert( child is self.__cornerWidget or child in self.__widgets )
		
		if child is self.__cornerWidget :
			self._qtWidget().setCornerWidget( None )
			self.__cornerWidget = None
		else :
			self._qtWidget().removeTab( self.__widgets.index( child ) )
			self.__widgets.remove( child )

		child._qtWidget().setParent( None )
		child._applyVisibility()
		
	def setCornerWidget( self, cornerWidget ) :
	
		if self.__cornerWidget is not None :
			self.removeChild( self.__cornerWidget )
			
		if cornerWidget is not None :
			oldParent = cornerWidget.parent()
			if oldParent is not None :
				oldParent.removeChild( cornerWidget )
			self._qtWidget().setCornerWidget( cornerWidget._qtWidget() )
			cornerWidget._applyVisibility()
			assert( cornerWidget._qtWidget().parent() is self._qtWidget() )
		else :
			self._qtWidget().setCornerWidget( None )
			
		self.__cornerWidget = cornerWidget
		
	def getCornerWidget( self ) :
	
		return self.__cornerWidget
		
	def setTabsVisible( self, visible ) :
	
		self._qtWidget().tabBar().setVisible( visible )
		
	def getTabsVisible( self ) :
	
		return not self._qtWidget().tabBar().isHidden()
		
	def currentChangedSignal( self ) :
	
		return self.__currentChangedSignal
		
	def __currentChanged( self, index ) :
		
		self.__currentChangedSignal( self, self[index] )
		
