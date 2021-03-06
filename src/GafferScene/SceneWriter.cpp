//////////////////////////////////////////////////////////////////////////
//  
//  Copyright (c) 2013-2014, Image Engine Design inc. All rights reserved.
//  
//  Redistribution and use in source and binary forms, with or without
//  modification, are permitted provided that the following conditions are
//  met:
//  
//      * Redistributions of source code must retain the above
//        copyright notice, this list of conditions and the following
//        disclaimer.
//  
//      * Redistributions in binary form must reproduce the above
//        copyright notice, this list of conditions and the following
//        disclaimer in the documentation and/or other materials provided with
//        the distribution.
//  
//      * Neither the name of John Haddon nor the names of
//        any other contributors to this software may be used to endorse or
//        promote products derived from this software without specific prior
//        written permission.
//  
//  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
//  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
//  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
//  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
//  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
//  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
//  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
//  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
//  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
//  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
//  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//  
//////////////////////////////////////////////////////////////////////////

#include "IECore/SceneInterface.h"
#include "IECore/Transform.h"

#include "Gaffer/ScriptNode.h"

#include "GafferScene/SceneWriter.h"

using namespace std;
using namespace IECore;
using namespace Gaffer;
using namespace GafferScene;

IE_CORE_DEFINERUNTIMETYPED( SceneWriter );

/// \todo hard coded framerate should be replaced with a getTime() method on Gaffer::Context or something
const double SceneWriter::g_frameRate( 24 );

size_t SceneWriter::g_firstPlugIndex = 0;

SceneWriter::SceneWriter( const std::string &name )
	: ExecutableNode( name )
{
	storeIndexOfNextChild( g_firstPlugIndex );
	addChild( new ScenePlug( "in", Plug::In ) );
	addChild( new StringPlug( "fileName" ) );
}

SceneWriter::~SceneWriter()
{
}

ScenePlug *SceneWriter::inPlug()
{
	return getChild<ScenePlug>( g_firstPlugIndex );
}

const ScenePlug *SceneWriter::inPlug() const
{
	return getChild<ScenePlug>( g_firstPlugIndex );
}

StringPlug *SceneWriter::fileNamePlug()
{
	return getChild<StringPlug>( g_firstPlugIndex + 1 );
}

const StringPlug *SceneWriter::fileNamePlug() const
{
	return getChild<StringPlug>( g_firstPlugIndex + 1 );
}

IECore::MurmurHash SceneWriter::executionHash( const Gaffer::Context *context ) const
{
	/// \todo How do we cheaply hash something representing the whole scene?
	/// Do we just hash the identity of the input node?
	return IECore::MurmurHash();
}

void SceneWriter::execute( const Contexts &contexts ) const
{
	const ScenePlug *scene = inPlug()->getInput<ScenePlug>();
	if( !scene )
	{
		throw IECore::Exception( "No input scene" );
	}
	
	SceneInterfacePtr output = SceneInterface::create( fileNamePlug()->getValue(), IndexedIO::Write );
	
	for ( Contexts::const_iterator it = contexts.begin(), eIt = contexts.end(); it != eIt; it++ )
	{
		ContextPtr context = new Context( *it->get(), Context::Borrowed );
		Context::Scope scopedContext( context );
		double time = context->getFrame() / g_frameRate;
		writeLocation( scene, ScenePlug::ScenePath(), context, output.get(), time );
	}
}

void SceneWriter::writeLocation( const GafferScene::ScenePlug *scene, const ScenePlug::ScenePath &scenePath, Context *context, IECore::SceneInterface *output, double time ) const
{
	context->set( ScenePlug::scenePathContextName, scenePath );
	
	ConstCompoundObjectPtr attributes = scene->attributesPlug()->getValue();
	for( CompoundObject::ObjectMap::const_iterator it = attributes->members().begin(), eIt = attributes->members().end(); it != eIt; it++ )
	{
		output->writeAttribute( it->first, it->second.get(), time );
	}
	
	if( scenePath.empty() )
	{
		ConstCompoundObjectPtr globals = scene->globalsPlug()->getValue();
		output->writeAttribute( "gaffer:globals", globals, time );
	}
	
	ConstObjectPtr object = scene->objectPlug()->getValue();
	
	if( object->typeId() != IECore::NullObjectTypeId && scenePath.size() > 0 )
	{
		output->writeObject( object, time );
	}
	
	Imath::Box3f b = scene->boundPlug()->getValue();
	
	output->writeBound( Imath::Box3d( Imath::V3f( b.min ), Imath::V3f( b.max ) ), time );
	
	if( scenePath.size() )
	{
		Imath::M44f t = scene->transformPlug()->getValue();
		Imath::M44d transform(
			t[0][0], t[0][1], t[0][2], t[0][3],
			t[1][0], t[1][1], t[1][2], t[1][3],
			t[2][0], t[2][1], t[2][2], t[2][3],
			t[3][0], t[3][1], t[3][2], t[3][3]
		);

		output->writeTransform( new IECore::M44dData( transform ), time );
	}
	
	ConstInternedStringVectorDataPtr childNames = scene->childNamesPlug()->getValue();
	
	ScenePlug::ScenePath childScenePath = scenePath;
	childScenePath.push_back( InternedString() );
	for( vector<InternedString>::const_iterator it=childNames->readable().begin(); it!=childNames->readable().end(); it++ )
	{
		childScenePath[scenePath.size()] = *it;
		
		SceneInterfacePtr outputChild = output->createChild( *it );
		
		writeLocation( scene, childScenePath, context, outputChild, time );
	}
}
